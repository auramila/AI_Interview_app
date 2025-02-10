import os
import re
import time
import streamlit as st
import openai
from dotenv import load_dotenv


st.set_page_config(page_title="🤖 AI Interview Coach", page_icon="💼", layout="centered")

# Custom Styling with HTML/CSS
st.markdown(
    """
    <style>
    /* Import Google Fonts: Montserrat for headings and Open Sans for body */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap');

    /* Overall app styling */
    .stApp {
         background: linear-gradient(135deg, #000000, #141414);
         color: #F1FAEE;
         font-family: 'Open Sans', sans-serif;
         padding: 1rem;
    }
    /* Sidebar styling */
    .stSidebar {
         background-color: #1A1A1A;
         color: #F1FAEE;
         padding: 1.5rem;
         box-shadow: 2px 0 8px rgba(0,0,0,0.3);
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
         color: #E63946;
         font-family: 'Montserrat', sans-serif;
    }
    /* Button styling (Pink buttons with warmer hover; text remains white) */
    .stButton > button {
         background-color: #E63946;
         color: #F1FAEE;
         border: none;
         border-radius: 8px;
         padding: 0.6rem 1.2rem;
         font-size: 1rem;
         transition: background-color 0.3s ease, transform 0.2s ease;
         cursor: pointer;
         box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .stButton > button:hover {
         background-color: #F16A67;
         transform: translateY(-2px);
         color: #F1FAEE;
    }
    /* Text area styling */
    .stTextArea > div > textarea {
         background-color: #333;
         border: 1px solid #444;
         border-radius: 5px;
         color: #F1FAEE;
         padding: 0.7rem;
    }
    /* Header styling */
    h1, h2, h3, h4, h5, h6 {
         font-family: 'Montserrat', sans-serif;
         color: #E63946;
    }
    /* Progress bar styling */
    .css-1aumxhk {
         background-color: #444;
    }
    .css-1aumxhk > div {
         background-color: #E63946;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Helper Functions for Security
def is_safe_input(text):
    """
    Check for potentially malicious content.
    Disallow common HTML/script patterns.
    """
    if re.search(r'<\s*script', text, re.IGNORECASE):
        return False
    if re.search(r'<\s*img', text, re.IGNORECASE):
        return False
    if re.search(r'<\s*iframe', text, re.IGNORECASE):
        return False
    if re.search(r'onerror\s*=', text, re.IGNORECASE):
        return False
    return True

def sanitize_input(user_input):
    s = user_input.strip()
    return s[:1000] if len(s) > 1000 else s

def retry_api_call(api_func, max_attempts=3, delay=1, **kwargs):
    """
    Simple retry mechanism for OpenAI API calls.
    """
    for attempt in range(max_attempts):
        try:
            return api_func(**kwargs)
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(delay)
            else:
                raise e

# --- Environment Setup ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("API key not found. Please set the OPENAI_API_KEY environment variable.")
    st.stop()
openai.api_key = api_key

# --- Sidebar for User Inputs ---
st.sidebar.title("AI Interview Coach")
st.sidebar.markdown("Fill in your details")

predefined_roles = ["Product Manager", "Software Engineer", "Data Scientist", "Marketing Manager", "UX Designer"]
predefined_companies = ["Google", "Amazon", "Vinted", "Meta", "Startups"]

role_choice = st.sidebar.selectbox("Your Role", predefined_roles + ["Other"])
if role_choice == "Other":
    role = st.sidebar.text_input("Enter your role", value="")
    if role == "":
        role = "Custom Role"
    elif not is_safe_input(role):
        st.error("Invalid role input detected. Please remove any HTML or script content.")
        st.stop()
else:
    role = role_choice

company_choice = st.sidebar.selectbox("Target Company", predefined_companies + ["Other"])
if company_choice == "Other":
    company = st.sidebar.text_input("Enter target company", value="")
    if company == "":
        company = "Custom Company"
    elif not is_safe_input(company):
        st.error("Invalid company input detected. Please remove any HTML or script content.")
        st.stop()
else:
    company = company_choice

job_description = st.sidebar.text_area(
    "Job Description (Optional)",
    value="",
    help="Enter the job description for the position you are applying for. This will help tailor the interview questions."
)

num_questions = st.sidebar.selectbox("Number of Interview Questions", list(range(1, 11)))

# --- Advanced Settings ---
with st.sidebar.expander("Advanced Settings (Techy Stuff)"):
    temperature = st.slider(
        "Temperature", 0.0, 1.0, 0.7, 0.05,
        help="Controls randomness. Lower values yield more deterministic responses; higher values yield more creative outputs."
    )
    top_p = st.slider(
        "Top-p", 0.0, 1.0, 1.0, 0.05,
        help="Controls diversity via nucleus sampling. Lower values narrow the output."
    )
    frequency_penalty = st.slider(
        "Frequency Penalty", 0.0, 2.0, 0.0, 0.1,
        help="Penalizes repetition to keep things fresh."
    )
    question_prompt_type = st.selectbox(
        "Question Generation Technique",
        ["Zero-shot", "Few-shot", "Chain-of-Thought", "Role-Specific", "Comparative"]
    )
    evaluation_prompt_type = st.selectbox(
        "Answer Evaluation Technique",
        ["Zero-shot", "Few-shot", "Chain-of-Thought", "Role-Specific", "Comparative"]
    )
    prompt_explanations = {
        "Zero-shot": "Direct and simple. No examples needed.",
        "Few-shot": "A couple of examples to steer the output in the right direction.",
        "Chain-of-Thought": "Break it down: get the model to think step-by-step.",
        "Role-Specific": "Customized details to match your role and company vibe.",
        "Comparative": "Compares your answer to an ideal response for feedback."
    }
    st.markdown(
        f"<small><b>Selected Technique ({question_prompt_type}):</b> {prompt_explanations.get(question_prompt_type)}</small>",
        unsafe_allow_html=True,
    )
    show_prompts = st.checkbox("Show System Prompts", value=False)

# --- Reset Session Button with Defaults ---
def reset_defaults():
    keys_to_reset = [
        "role",
        "company",
        "job_description",
        "num_questions",
        "temperature",
        "top_p",
        "frequency_penalty",
        "question_prompt_type",
        "evaluation_prompt_type",
        "history"
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.write("Reset complete. Please refresh the page to see default settings.")

if st.sidebar.button("Reset Session", on_click=reset_defaults):
    pass

# --- Main Title & Introduction ---
st.markdown("<h1 style='color: #E63946;'>🤖 AI Interview Coach</h1>", unsafe_allow_html=True)
st.markdown(f"""
Welcome to AI Interview Coach – your AI-powered tool to help you ace interviews!
Practice with real-world questions and get constructive feedback.

**How to use:**
1. Fill in your details (and add a job description for tailor-made questions) in the sidebar.
2. Tweak the advanced settings if you want to customize your experience.
3. Click the button below to generate your first question and start your interview journey.

Let's crush it!
""")

if "history" not in st.session_state:
    st.session_state.history = []

# --- Define System Prompts (Incorporating Job Description) ---
job_desc_clause = f" The job description is: {job_description}." if job_description.strip() != "" else ""

question_prompts = {
    "Zero-shot": f"You are an expert interviewer at {company} for a {role} position.{job_desc_clause} Generate a challenging yet realistic interview question for the user.",
    "Few-shot": (
        f"Below are sample interview questions and ideal answers for a {role} at {company}.{job_desc_clause}\n"
        "Q: Tell me about yourself?\nA: I have a strong background in ...\n"
        "Q: What are your strengths?\nA: I excel at problem-solving and teamwork.\n\n"
        "Now, generate a similar challenging interview question."
    ),
    "Chain-of-Thought": (
        f"Imagine you are a seasoned interviewer at {company} for a {role} role.{job_desc_clause} Think step-by-step and generate a detailed, challenging interview question, explaining your reasoning internally."
    ),
    "Role-Specific": (
        f"As a hiring manager at {company} interviewing for a {role}.{job_desc_clause} Create a highly specific question that tests the key skills required for this role."
    ),
    "Comparative": (
        f"Generate an interview question for a {role} at {company}.{job_desc_clause} Challenge the candidate and implicitly compare their answer to industry standards."
    )
}

evaluation_prompts = {
    "Zero-shot": (
        "You are a professional interview evaluator. Evaluate the user's answer based on clarity, depth, relevance, and conciseness. Provide a numeric score out of 10 in the format 'Score: <number>', followed by constructive feedback."
    ),
    "Few-shot": (
        "Here is an example evaluation:\n"
        "Question: How do you handle tight deadlines?\n"
        "Answer: I prioritize tasks and communicate effectively with my team.\n"
        "Score: 8. Feedback: Good clarity but consider adding more detail on your process.\n\n"
        "Now, evaluate the following answer with a similar approach."
    ),
    "Chain-of-Thought": (
        "Think step-by-step like a seasoned interviewer evaluating a candidate. Explain your reasoning and provide a numeric score along with detailed feedback on clarity, depth, and relevance."
    ),
    "Role-Specific": (
        f"As an interviewer for a {role} at {company}, evaluate the answer for its technical/behavioral depth, accuracy, and relevance. Provide a numeric score and detailed feedback."
    ),
    "Comparative": (
        "Compare the candidate's answer with the ideal response. Provide a numeric score (out of 10) and constructive feedback highlighting strengths and areas for improvement."
    )
}

if show_prompts:
    st.subheader("Current System Prompts")
    st.markdown("**Question Generation Prompt:**")
    st.code(question_prompts.get(question_prompt_type, ""), language="text")
    st.markdown("**Answer Evaluation Prompt:**")
    st.code(evaluation_prompts.get(evaluation_prompt_type, ""), language="text")

# --- Functions to Interact with the OpenAI API ---
def generate_question(role, company):
    sys_prompt = question_prompts.get(question_prompt_type, "")
    try:
        response = retry_api_call(
            openai.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": "Generate a question for me."}
            ],
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error("Error generating question. Please try again later.")
        return "Error: Unable to generate question."

def evaluate_answer(question, answer):
    ans = sanitize_input(answer)
    if not is_safe_input(ans):
        st.error("Suspicious input detected. Please remove any HTML or script content from your answer.")
        return "Error: Unsafe input."
    sys_prompt = evaluation_prompts.get(evaluation_prompt_type, "")
    try:
        response = retry_api_call(
            openai.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"Question: {question}\nAnswer: {ans}"}
            ],
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error("Error evaluating answer. Please try again later.")
        return "Error: Unable to evaluate answer."

def submit_answer_callback(index, answer_key):
    ans = st.session_state.get(answer_key, "").strip()
    if not ans:
        st.error("Please provide an answer before submitting.")
    else:
        feedback = evaluate_answer(st.session_state.history[index]["question"], ans)
        st.session_state.history[index]["answer"] = ans
        st.session_state.history[index]["feedback"] = feedback
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
        else:
            st.write("Reset complete. Please refresh the page to see changes.")

def add_question():
    new_question = generate_question(role, company)
    st.session_state.history.append({
        "question": new_question,
        "answer": None,
        "feedback": None
    })

# --- Interview Questions Display and Interaction ---
st.header("Interview Progress & Questions")

answered_count = sum(1 for item in st.session_state.history if item.get("answer") and item.get("answer").strip())
generated_count = len(st.session_state.history)
if generated_count > 0:
    st.markdown(f"**Progress:** {answered_count}/{generated_count} questions answered")
    st.progress(answered_count / generated_count if generated_count > 0 else 0)

if st.session_state.history:
    total_score = 0
    for i, qa_item in enumerate(st.session_state.history, start=1):
        st.subheader(f"Question {i}")
        st.write(f"**{qa_item['question']}**")
        answer_key = f"answer_{i}"
        user_answer = st.text_area("Your Answer", key=answer_key, value=qa_item["answer"] or "", height=100)
        submit_key = f"submit_{i}"
        st.button("Submit Answer", key=submit_key, on_click=submit_answer_callback, args=(i-1, answer_key))
        if qa_item.get("answer"):
            st.markdown(f"**Your Final Answer:**\n{qa_item['answer']}")
        if qa_item.get("feedback"):
            st.markdown(f"**AI Feedback:**\n{qa_item['feedback']}")
            try:
                score_line = qa_item['feedback'].split("Score:")[-1].strip().split(" ")[0]
                score = int(score_line)
                total_score += score
            except (ValueError, IndexError):
                pass
        st.divider()
    if answered_count > 0:
        avg_score = total_score / answered_count
        if avg_score >= 8:
            emoji = "🏆"
        elif avg_score >= 5:
            emoji = "👍"
        else:
            emoji = "😞"
        st.markdown("### Overall Performance Summary")
        st.write(f"**Average Score:** {avg_score:.1f} / 10 {emoji}")
        st.write("""
        **Areas of Improvement:**
        - Review your feedback for each question carefully.
        - Focus on clarity, depth, and relevance.
        - Practice delivering concise yet thorough answers.
        """)
        with st.expander("Recommended Learning Resources"):
            st.markdown("- [How to answer behavioral interview questions](https://www.themuse.com/advice/star-interview-method)")
            st.markdown("- [Improving technical interview skills](https://www.interviewcake.com/)")
            st.markdown("- [Common PM interview questions](https://www.productmanagementexercises.com/)")
else:
    st.info("No questions yet! Get your first interview question.")

# --- Get Next Interview Question Section ---
if generated_count == 0:
    st.header("Generate Your First Interview Question")
    st.markdown("Click the button below to kick off your interview practice!")
    st.button("Get First Interview Question", on_click=add_question)
elif generated_count < num_questions:
    st.header("Get Your Next Question")
    st.markdown("Generate the next question whenever you're ready to keep practicing!")
    st.button("Get Next Interview Question", on_click=add_question)
else:
    st.success("You've reached the requested number of questions! Reset session if you want to practise more.")
