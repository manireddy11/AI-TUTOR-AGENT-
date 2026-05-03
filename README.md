
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

![Alt text for your image](https://github.com/manireddy11/AI-TUTOR-AGENT-/raw/348d8a8a9000423fb8716a85598f243d3ae22a94/assets/Screenshot%202026-05-03%20162645.png)

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

![Catalog View](https://github.com/manireddy11/AI-TUTOR-AGENT-/raw/1d700479dba43e16d86b06b18aa69916574f79b0/assets/Screenshot%202026-05-03%20162645.png)

erDiagram
    users ||--o{ topic_progress : has
    users ||--o{ chat_history : has
    users ||--o{ mcq_attempts : makes
    users ||--o{ code_attempts : submits
    users ||--o{ personal_guide : uses

![Dashboard](https://github.com/manireddy11/AI-TUTOR-AGENT-/raw/1d700479dba43e16d86b06b18aa69916574f79b0/assets/Screenshot%202026-05-03%20162755.png)

---

![Mermaid Diagram](https://github.com/manireddy11/AI-TUTOR-AGENT-/raw/1d700479dba43e16d86b06b18aa69916574f79b0/assets/deepseek_mermaid_20260503_2aeaa9.png)


## 🧰 Tech Stack

| Layer          | Technology                                                                 |
|----------------|-----------------------------------------------------------------------------|
| **Frontend**   | Streamlit (custom CSS, session state, chat elements)                       |
| **LLM**        | Groq Cloud – LLaMA 3.1 8B (fast inference, streaming)                      |
| **Database**   | Supabase (PostgreSQL) – users, progress, chat history, quiz attempts       |
| **Auth**       | SHA‑256 password hashing + user UUIDs                                      |
| **Deployment** | Streamlit Community Cloud / any Docker‑ready host                          |

---


![Quiz Interface](https://github.com/manireddy11/AI-TUTOR-AGENT-/raw/1d700479dba43e16d86b06b18aa69916574f79b0/assets/Screenshot%202026-05-03%20162721.png)



![Screenshot](https://github.com/manireddy11/AI-TUTOR-AGENT-/raw/3d19139822455dbfee405a7ca1dcb61618fd1926/assets/Screenshot%202026-05-03%20165447.png)


🗄️ Database Schema – Performance Tracking & Agent Data Flow
The application uses Supabase (PostgreSQL) as its persistence layer. All user data – from login credentials to every chat message, quiz attempt, and coding submission – is stored in the five tables below. The AI Tutor (the Python/Streamlit agent) interacts with these tables using the Supabase client, performing direct select, insert, upsert, and delete queries.

![Screenshot](https://github.com/manireddy11/AI-TUTOR-AGENT-/raw/3d19139822455dbfee405a7ca1dcb61618fd1926/assets/Screenshot%202026-05-03%20165813.png)


🔍 How the AI Tutor Agent Retrieves Data
The agent (Streamlit backend) uses the supabase Python client. Queries are always filtered by user_id to ensure data isolation.

1. Loading user progress (e.g., dashboard)
python
def db_get_progress(uid):
    res = db().table("topic_progress").select("*").eq("user_id", uid).execute()
    return res.data
The result is cached in st.session_state.progress to reduce database round‑trips.

2. Updating progress after a quiz or lesson
python
def db_save_progress(uid, topic, subtopic, status, score=None):
    payload = {
        "user_id": uid, "topic": topic, "subtopic": subtopic,
        "status": status, "score": score,
        "completed_at": datetime.now(timezone.utc).isoformat() if status == "completed" else None
    }
    db().table("topic_progress").upsert(payload, on_conflict="user_id,topic,subtopic").execute()
upsert = insert or update. If a user retakes a quiz, the new score and status overwrite the old ones – the latest attempt defines progress.

3. Retrieving chat history for the Personal Teacher sidebar
python
def db_load_guide_messages(uid):
    res = db().table("personal_guide").select("role,content,created_at")\
              .eq("user_id", uid).order("created_at").execute()
    return res.data or []
Messages are loaded in chronological order and passed to the LLM (Groq) as conversation context – the AI remembers previous questions in the session.

4. Aggregating performance for the dashboard
The agent fetches raw records (e.g., all topic_progress entries for a user) and performs aggregations in Python – counting completed topics, averaging scores, building course‑by‑course breakdowns. This keeps SQL queries simple and portable.


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
