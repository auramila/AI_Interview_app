# 🤖 AI Interview Coach – Master Your Interviews with AI

## Introduction

AI Interview Coach is an **AI-powered interview preparation tool** designed to help users practice real-world interview questions, receive **instant AI feedback**, and refine their answers for top performance. The app is powered by **Streamlit** and OpenAI’s GPT models, allowing for **customized, role-specific** question generation and evaluation.

## Key Objectives

- **Generate interview questions** tailored to your role and target company.
- **Evaluate answers in real-time** with AI-powered scoring and feedback.
- **Customize AI behavior** using adjustable parameters like **temperature, top-p, and frequency penalties**.
- **Enhance interview readiness** by simulating real interview conditions.


With this tool, you can refine your interview skills by testing different response strategies and **learning from AI-generated feedback**.

---

## Features

- 🎯 **Role & Company-Specific Questions** – Select your role and target company for tailored questions.
- 🤖 **AI-Driven Answer Evaluation** – Get immediate feedback with numeric scoring and suggestions.
- 🔥 **Advanced AI Techniques** – Choose from **Zero-shot, Few-shot, Chain-of-Thought, Role-Specific, and Comparative** questioning styles.
- 📜 **Session Tracking** – Track your past questions, answers, and feedback for improvement.

---

## Data Overview

### API Usage

The app relies on **OpenAI’s GPT API** to generate and evaluate interview questions dynamically.
Ensure you have a valid **OpenAI API key** to use this tool.

---

## Installation and Setup

1. Clone the Repository

```markdown
git clone git@github.com:auramila/AI_Interview_app.git
```

2. Install dependencies

```markdown
pip install -r requirements.txt
```

3. Set Up Environment Variables

Create a .env file in the root directory and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

4. Run the Application

```markdown
streatlit run interview_app
```


## Authors

**Aura Milasiute** - [GitHub](https://github.com/auramila)

## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/)
