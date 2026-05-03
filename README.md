
<!-- markdownlint-disable MD033 -->
<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Groq-LLaMA%203.1%208B-FF6B6B?logo=groq&logoColor=white" alt="Groq">
  <img src="https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase&logoColor=white" alt="Supabase">
  <br/>
  <img src="https://img.shields.io/badge/status-active-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="License">
</div>

<h1 align="center" style="background: linear-gradient(135deg, #dc2626, #b91c1c); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 2.8rem;">TEACHER.AI</h1>
<p align="center"><strong>An advanced AI‑powered learning system with personal guidance & progress tracking</strong><br/>Powered by Groq LLaMA 3.1, Supabase, and Streamlit</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-database-schema">Database Schema</a> •
  <a href="#-courses">Courses</a>
</p>

---

## ✨ Features

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem;">
  <div style="background: #f8f9fa; border-radius: 1rem; padding: 1rem;">
    <strong>🎓 8 Expert Courses</strong><br/>MLOps, LLM fine‑tuning, cloud, databases, software engineering & more.
  </div>
  <div style="background: #f8f9fa; border-radius: 1rem; padding: 1rem;">
    <strong>🤖 AI‑Generated Lessons</strong><br/>Dynamic content for each topic, with real‑world examples and code.
  </div>
  <div style="background: #f8f9fa; border-radius: 1rem; padding: 1rem;">
    <strong>📝 Adaptive Quizzes</strong><br/>Auto‑generated MCQs with instant scoring and explanations.
  </div>
  <div style="background: #f8f9fa; border-radius: 1rem; padding: 1rem;">
    <strong>🧑‍🏫 Personal Teacher</strong><br/>Chat sidebar – ask anything about your courses or learning path.
  </div>
  <div style="background: #f8f9fa; border-radius: 1rem; padding: 1rem;">
    <strong>📊 Progress Dashboard</strong><br/>Track completed topics, average quiz scores, and course completion.
  </div>
  <div style="background: #f8f9fa; border-radius: 1rem; padding: 1rem;">
    <strong>🔐 Secure Authentication</strong><br/>Password hashing (SHA‑256) and user‑specific data isolation.
  </div>
</div>



erDiagram
    users ||--o{ topic_progress : has
    users ||--o{ chat_history : has
    users ||--o{ mcq_attempts : makes
    users ||--o{ code_attempts : submits
    users ||--o{ personal_guide : uses



---

## 🧰 Tech Stack

| Layer          | Technology                                                                 |
|----------------|-----------------------------------------------------------------------------|
| **Frontend**   | Streamlit (custom CSS, session state, chat elements)                       |
| **LLM**        | Groq Cloud – LLaMA 3.1 8B (fast inference, streaming)                      |
| **Database**   | Supabase (PostgreSQL) – users, progress, chat history, quiz attempts       |
| **Auth**       | SHA‑256 password hashing + user UUIDs                                      |
| **Deployment** | Streamlit Community Cloud / any Docker‑ready host                          |

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- A [Groq API Key](https://console.groq.com)
- A [Supabase Project](https://supabase.com) (PostgreSQL)

### 2. Clone & Install

```bash
git clone https://github.com/yourusername/teacher-ai.git
cd teacher-ai
pip install -r requirements.txt
