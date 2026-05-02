"""
TEACHER.AI – Production v5.0
Backend: Groq (Llama 3.1 8B Instant)  |  DB: Supabase  |  Theme: Stanford White + Red
Fixes: Dashboard transparency, metric colors, all 10 production bugs patched.
Courses: New 2026 curriculum (8 courses).  Code tab removed, sign‑out in sidebar,
        no emoji icons in course titles, renamed to TEACHER.AI.
"""

import os, re, json, uuid, hashlib, ast, io, contextlib, traceback as tb_module
import streamlit as st
from datetime import datetime, timezone
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ─── PAGE CONFIG ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="TEACHER.AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── SECRETS ─────────────────────────────────────────────────────────
def _secret(key, default=""):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)

GROQ_API_KEY = _secret("GROQ_API_KEY")
SUPABASE_URL = _secret("SUPABASE_URL")
SUPABASE_KEY = _secret("SUPABASE_KEY")
MODEL = "llama-3.1-8b-instant"

def _render_html(html):
    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────
_render_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg: #ffffff;
  --bg-offset: #fafbfc;
  --card: #ffffff;
  --border: #eef2f6;
  --border2: #e2e8f0;
  --text: #1a202c;
  --text-light: #2d3748;
  --text-muted: #4a5568;
  --primary: #dc2626;
  --primary-dark: #b91c1c;
  --primary-light: #fee2e2;
  --primary-bg: #fff5f5;
  --success: #16a34a;
  --success-bg: #f0fdf4;
  --warning: #d97706;
  --warning-bg: #fffbeb;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.02);
  --shadow: 0 4px 12px rgba(0,0,0,0.03);
  --shadow-lg: 0 20px 30px -12px rgba(0,0,0,0.08);
  --radius: 20px;
  --radius-sm: 14px;
  --radius-xs: 10px;
}

html, body, [class*="css"] {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}
.stApp { background: var(--bg) !important; }
.block-container { max-width: 1440px !important; padding: 1rem 2rem 2rem !important; }

[data-testid="stSidebar"] {
  background: var(--bg) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div {
  background: var(--bg) !important;
  padding: 1rem 0.5rem !important;
}

/* ── BUTTONS ── */
.stButton > button {
  border-radius: 40px !important;
  font-weight: 500 !important;
  font-size: 0.85rem !important;
  padding: 0.5rem 1.2rem !important;
  transition: all 0.2s ease !important;
  background: white !important;
  border: 1px solid var(--border2) !important;
  color: var(--text-light) !important;
  box-shadow: var(--shadow-sm);
}
.stButton > button[kind="primary"] {
  background: var(--primary) !important;
  border: none !important;
  color: white !important;
  -webkit-text-fill-color: white !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--primary-dark) !important;
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}
.stButton > button:hover:not([kind="primary"]) {
  border-color: var(--primary) !important;
  color: var(--primary) !important;
  background: var(--primary-bg) !important;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea textarea,
[data-testid="stChatInput"] textarea {
  background: var(--bg-offset) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 20px !important;
  padding: 0.7rem 1rem !important;
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  font-size: 0.9rem !important;
  opacity: 1 !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus,
[data-testid="stChatInput"] textarea:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px var(--primary-light) !important;
  outline: none;
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] .stMarkdown p {
  color: var(--text) !important;
}
[data-testid="stChatMessage-user"] .stMarkdown {
  background: var(--primary) !important;
  border-radius: 24px 24px 4px 24px !important;
  padding: 12px 18px !important;
}
[data-testid="stChatMessage-user"] .stMarkdown p {
  color: white !important;
  -webkit-text-fill-color: white !important;
}
[data-testid="stChatMessage-assistant"] .stMarkdown {
  background: var(--bg-offset) !important;
  border-left: 3px solid var(--primary) !important;
  border-radius: 0 24px 24px 0 !important;
  padding: 12px 18px !important;
}

/* ── LESSON CONTENT ── */
.stMarkdown p,
.stMarkdown li,
.stMarkdown h1,
.stMarkdown h2,
.stMarkdown h3,
.stMarkdown h4 {
  color: var(--text) !important;
}

/* ── AUTH CARD ── */
div[data-testid="stRadio"] label,
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] label span,
div[data-baseweb="radio"] label,
div[data-baseweb="radio"] label * {
  color: var(--text) !important;
  opacity: 1 !important;
}
div[data-testid="stRadio"] label[data-checked="true"],
div[data-testid="stRadio"] label[aria-checked="true"] {
  background: var(--primary) !important;
  border-color: var(--primary) !important;
  color: white !important;
}
div[data-testid="stRadio"] label[data-checked="true"] *,
div[data-testid="stRadio"] label[aria-checked="true"] * {
  color: white !important;
  -webkit-text-fill-color: white !important;
}
div[data-testid="stForm"] input,
div[data-testid="stForm"] label,
div[data-testid="stForm"] label p {
  color: var(--text) !important;
  opacity: 1 !important;
  -webkit-text-fill-color: var(--text) !important;
}
div[data-testid="stForm"] input::placeholder {
  color: var(--text-muted) !important;
  -webkit-text-fill-color: var(--text-muted) !important;
  opacity: 0.7 !important;
}
div[data-testid="stForm"] button[kind="primaryFormSubmit"],
div[data-testid="stForm"] button[kind="primary"] {
  background: var(--primary) !important;
  color: white !important;
  -webkit-text-fill-color: white !important;
  opacity: 1 !important;
}
[data-baseweb="input"] input,
[data-baseweb="base-input"] input {
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  opacity: 1 !important;
  background: white !important;
}
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span {
  opacity: 1 !important;
  color: inherit !important;
}

/* ── DASHBOARD: st.metric transparency fix ── */
[data-testid="stMetric"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 16px !important;
  padding: 1.2rem 1.4rem !important;
  box-shadow: var(--shadow) !important;
}
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] span {
  color: var(--text-muted) !important;
  font-size: 0.75rem !important;
  font-weight: 500 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  opacity: 1 !important;
  -webkit-text-fill-color: var(--text-muted) !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] p,
[data-testid="stMetricValue"] span {
  color: var(--text) !important;
  font-size: 2rem !important;
  font-weight: 600 !important;
  line-height: 1.2 !important;
  opacity: 1 !important;
  -webkit-text-fill-color: var(--text) !important;
}
[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] p,
[data-testid="stMetricDelta"] span {
  opacity: 1 !important;
  font-size: 0.78rem !important;
  font-weight: 500 !important;
}
[data-testid="stMetricDelta"][data-direction="up"] svg,
[data-testid="stMetricDelta"][data-direction="up"] span {
  color: var(--success) !important;
  -webkit-text-fill-color: var(--success) !important;
}
[data-testid="stMetricDelta"][data-direction="down"] svg,
[data-testid="stMetricDelta"][data-direction="down"] span {
  color: var(--primary) !important;
  -webkit-text-fill-color: var(--primary) !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
}

/* ── CODE BLOCKS ── */
.stMarkdown pre, .stMarkdown code {
  background: #f8f9fa !important;
  border-radius: 12px !important;
  font-family: 'JetBrains Mono', monospace !important;
  color: var(--text) !important;
}

/* ── PROGRESS BARS ── */
hr { border-color: var(--border) !important; margin: 1rem 0; }
[data-testid="stProgress"] > div { background-color: var(--border2) !important; border-radius: 50px; }
[data-testid="stProgress"] > div > div { background-color: var(--primary) !important; border-radius: 50px; }

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header, .stDeployButton, [data-testid="stToolbar"] { display: none !important; }

/* ── PERSONAL TEACHER ── */
.teacher-bar {
  background: var(--bg-offset);
  border-top: 1px solid var(--border);
  border-radius: 20px;
  padding: 1.2rem 1.4rem;
  margin-top: 2rem;
  box-shadow: var(--shadow);
}
.teacher-bar [data-testid="stChatInput"] textarea {
  background: white !important;
  -webkit-text-fill-color: var(--text) !important;
}
</style>
""")

# ─── NEW 2026 COURSE CATALOG (8 courses, no emoji icons) ─────────────
COURSES = {
    "mlops": {
        "id": "mlops",
        "title": "MLOps & LLMOps",
        "tagline": "Operationalise AI models – the #1 scarce skill in 2026",
        "difficulty": "Advanced",
        "hours": 7,
        "modules": [
            {
                "title": "CI/CD & Model Serving",
                "topics": [
                    {"title": "CI/CD pipelines for ML with GitHub Actions", "min": 40},
                    {"title": "FastAPI for model serving", "min": 35},
                    {"title": "Docker & Kubernetes for ML workloads", "min": 45},
                    {"title": "MLflow for experiment tracking and registry", "min": 30},
                ]
            },
            {
                "title": "Monitoring & Observability",
                "topics": [
                    {"title": "Training monitoring with Weights & Biases", "min": 35},
                    {"title": "Data drift detection with WhyLabs", "min": 30},
                    {"title": "Model performance monitoring and alerting", "min": 30},
                ]
            },
        ]
    },
    "llm_finetune": {
        "id": "llm_finetune",
        "title": "LLM Fine‑Tuning",
        "tagline": "Custom models from pre‑trained bases – most hired AI skill",
        "difficulty": "Advanced",
        "hours": 6,
        "modules": [
            {
                "title": "Foundational Techniques",
                "topics": [
                    {"title": "LoRA / QLoRA: theory and implementation", "min": 35},
                    {"title": "Hugging Face Transformers for fine‑tuning", "min": 40},
                    {"title": "Supervised Fine‑Tuning (SFT) on custom data", "min": 35},
                ]
            },
            {
                "title": "Advanced Alignment & Integration",
                "topics": [
                    {"title": "RLHF basics & preference alignment", "min": 35},
                    {"title": "Quantization for efficient deployment", "min": 30},
                    {"title": "RAG integration with fine‑tuned models", "min": 30},
                    {"title": "OpenAI fine‑tune API practical", "min": 25},
                ]
            },
        ]
    },
    "llm_scratch": {
        "id": "llm_scratch",
        "title": "Building an LLM from Scratch",
        "tagline": "Transformer internals to pre‑training – deep architectural knowledge",
        "difficulty": "Expert",
        "hours": 9,
        "modules": [
            {
                "title": "Transformer Architecture",
                "topics": [
                    {"title": "Tokenization: BPE, WordPiece, SentencePiece", "min": 35},
                    {"title": "Self‑attention and multi‑head attention", "min": 40},
                    {"title": "Positional encoding and embeddings", "min": 30},
                    {"title": "Complete GPT architecture walkthrough", "min": 45},
                ]
            },
            {
                "title": "Pre‑training & Scaling",
                "topics": [
                    {"title": "Implementing a pre‑training loop", "min": 40},
                    {"title": "Scaling laws and compute optimal training", "min": 30},
                    {"title": "Evaluation benchmarks and perplexity", "min": 25},
                ]
            },
        ]
    },
    "applied_ml": {
        "id": "applied_ml",
        "title": "Applied Machine Learning",
        "tagline": "Practical ML for IT pros – skip theory, focus on real pipelines",
        "difficulty": "Intermediate",
        "hours": 7,
        "modules": [
            {
                "title": "Core ML Pipelines",
                "topics": [
                    {"title": "Supervised vs unsupervised learning – when to use what", "min": 30},
                    {"title": "Feature engineering workshop", "min": 35},
                    {"title": "Scikit‑learn pipelines", "min": 30},
                    {"title": "XGBoost for tabular data", "min": 35},
                    {"title": "Model selection & cross‑validation", "min": 25},
                ]
            },
            {
                "title": "Deployment & Responsibility",
                "topics": [
                    {"title": "Serving models with FastAPI / Docker", "min": 30},
                    {"title": "Bias detection and fairness in ML", "min": 25},
                ]
            },
        ]
    },
    "ai_coding": {
        "id": "ai_coding",
        "title": "AI‑Assisted Coding",
        "tagline": "Code faster with DeepSeek v4 & Claude – massive time‑saver",
        "difficulty": "Beginner",
        "hours": 4,
        "modules": [
            {
                "title": "AI‑Powered Development",
                "topics": [
                    {"title": "Prompt patterns for code generation", "min": 25},
                    {"title": "Claude API for coding tasks", "min": 25},
                    {"title": "DeepSeek v4 API and use cases", "min": 25},
                    {"title": "AI code review workflows", "min": 20},
                    {"title": "Agentic coding: multi‑file refactoring", "min": 30},
                    {"title": "Test generation with AI", "min": 20},
                ]
            },
        ]
    },
    "cloud": {
        "id": "cloud",
        "title": "Cloud (AWS / Azure / GCP)",
        "tagline": "#1 upskilling area for IT professionals in 2026",
        "difficulty": "Intermediate",
        "hours": 9,
        "modules": [
            {
                "title": "Core Cloud Infrastructure",
                "topics": [
                    {"title": "AWS Solutions Architect essentials", "min": 40},
                    {"title": "Azure AZ‑900 → AZ‑104 path", "min": 35},
                    {"title": "Kubernetes (CKA) fundamentals", "min": 45},
                    {"title": "Infrastructure as Code with Terraform", "min": 35},
                ]
            },
            {
                "title": "Serverless & AI Services",
                "topics": [
                    {"title": "Serverless functions (AWS Lambda, Cloud Run, Azure Functions)", "min": 35},
                    {"title": "Cloud AI services: SageMaker, Azure AI, Vertex AI", "min": 30},
                ]
            },
        ]
    },
    "databases": {
        "id": "databases",
        "title": "Databases for AI Workloads",
        "tagline": "SQL to vector DBs – the missing link for data pipeline work",
        "difficulty": "Intermediate",
        "hours": 6,
        "modules": [
            {
                "title": "SQL & NoSQL",
                "topics": [
                    {"title": "SQL fundamentals and advanced queries", "min": 30},
                    {"title": "PostgreSQL for analytics", "min": 30},
                    {"title": "MongoDB document model and aggregation pipeline", "min": 25},
                ]
            },
            {
                "title": "Vector Databases & Data Modeling",
                "topics": [
                    {"title": "Introduction to vector databases (Pinecone, Qdrant)", "min": 30},
                    {"title": "Data modeling for AI/ML pipelines", "min": 25},
                    {"title": "Indexing strategies for high‑dimensional data", "min": 20},
                ]
            },
        ]
    },
    "software_eng": {
        "id": "software_eng",
        "title": "Modern Software Engineering",
        "tagline": "System design, clean code, and architecture for senior roles",
        "difficulty": "Advanced",
        "hours": 11,
        "modules": [
            {
                "title": "System Design & Patterns",
                "topics": [
                    {"title": "System design fundamentals", "min": 40},
                    {"title": "Design patterns for maintainable code", "min": 35},
                    {"title": "REST & GraphQL API design", "min": 30},
                ]
            },
            {
                "title": "Practices & Architecture",
                "topics": [
                    {"title": "Git workflows & trunk‑based development", "min": 25},
                    {"title": "Testing strategy: unit, integration, e2e", "min": 30},
                    {"title": "Microservices architecture patterns", "min": 35},
                    {"title": "DSA for technical interviews", "min": 40},
                ]
            },
        ]
    },
}

# ─── STATIC CODING TASKS (kept for compatibility) ────────────────────
BEGINNER_TASKS = [
    {"title": "Hello, World!", "description": "Print 'Hello, World!' to the console.", "expected_output": "Hello, World!", "difficulty": "beginner"},
    {"title": "Sum of Two Numbers", "description": "Given a=5, b=7, print their sum.", "expected_output": "12", "difficulty": "beginner"},
    {"title": "String Length", "description": "Print the length of the string 'AI Tutor'.", "expected_output": "8", "difficulty": "beginner"},
]
INTERMEDIATE_TASKS = [
    {"title": "FizzBuzz", "description": "Print numbers 1-20 separated by spaces. For multiples of 3 print 'Fizz', 5 print 'Buzz', both print 'FizzBuzz'.", "expected_output": "1 2 Fizz 4 Buzz Fizz 7 8 Fizz Buzz 11 Fizz 13 14 FizzBuzz 16 17 Fizz 19 Buzz", "difficulty": "intermediate"},
    {"title": "List Reversal", "description": "Reverse the list [1,2,3,4,5] and print it.", "expected_output": "[5, 4, 3, 2, 1]", "difficulty": "intermediate"},
]
ADVANCED_TASKS = [
    {"title": "Recursive Fibonacci", "description": "Print the 10th Fibonacci number (starting 0,1,...).", "expected_output": "55", "difficulty": "advanced"},
]
TASKS = {"beginner": BEGINNER_TASKS, "intermediate": INTERMEDIATE_TASKS, "advanced": ADVANCED_TASKS}

def get_random_task(difficulty):
    import random
    difficulty = difficulty.lower()
    if difficulty not in TASKS:
        difficulty = "beginner"
    return random.choice(TASKS[difficulty])

# ─── GROQ CLIENT ──────────────────────────────────────────────────────
@st.cache_resource
def _get_client():
    if not GROQ_API_KEY:
        raise RuntimeError("Set GROQ_API_KEY in secrets or .env")
    return Groq(api_key=GROQ_API_KEY)

def _compose_messages(messages, system):
    return [{"role": "system", "content": system}] + messages

def _call_llm(messages, system="You are an expert tutor.", max_tokens=1800, temp=0.5):
    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model=MODEL,
            messages=_compose_messages(messages, system),
            temperature=temp,
            max_tokens=max_tokens,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        return f"[LLM error: {e}]"

def _stream_llm(messages, system, max_tokens=2000):
    try:
        client = _get_client()
        stream = client.chat.completions.create(
            model=MODEL,
            messages=_compose_messages(messages, system),
            max_tokens=max_tokens,
            temperature=0.6,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as e:
        yield f"[Streaming error: {e}]"

def _extract_json_array(raw: str):
    raw = raw.strip()
    if raw.startswith("[LLM error:"): return None
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
    if not raw: return None
    try:
        return json.loads(raw)
    except Exception:
        m = re.search(r"\[.*\]", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except Exception:
                pass
    return None

# ─── SESSION STATE ────────────────────────────────────────────────────
_DEFAULTS = dict(
    authenticated=False, user_id=None, user_name=None, user_username=None,
    page="catalog", active_course=None, active_module_idx=0, active_topic_idx=0,
    active_mode="lesson",
    chat_messages={}, progress={},
    mcq_questions=[], mcq_answers={}, mcq_submitted=False, mcq_results=None,
    selected_task=None, user_code="", code_eval=None, code_submitted=False,
    code_difficulty="Beginner", new_task_selected=False,
    topic_content_cache={},
    guide_messages=[],
    guide_messages_loaded=False,
)
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── DATABASE ─────────────────────────────────────────────────────────
@st.cache_resource
def _supabase():
    if not SUPABASE_URL or not SUPABASE_KEY: return None
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def require_db():
    sb = _supabase()
    if not sb:
        st.error("🚨 Database not connected. Check Supabase secrets.")
        st.stop()
    return sb

def db():
    return require_db()

def db_save_guide_message(uid, role, content):
    try:
        db().table("personal_guide").insert({
            "user_id": uid, "role": role, "content": content,
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
    except Exception:
        pass

def db_load_guide_messages(uid):
    try:
        res = db().table("personal_guide").select("role,content,created_at")\
                  .eq("user_id", uid).order("created_at").execute()
        return res.data or []
    except Exception:
        return []

def db_create_user(uid, username, password_hash, name):
    try:
        return db().table("users").insert({
            "id": uid, "username": username,
            "password_hash": password_hash, "name": name,
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return None

def db_get_user(username):
    try:
        res = db().table("users").select("*").eq("username", username).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None

def db_get_user_by_id(uid):
    try:
        res = db().table("users").select("*").eq("id", uid).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None

def db_save_chat(uid, topic, role, content):
    try:
        return db().table("chat_history").insert({
            "user_id": uid, "topic": topic, "role": role,
            "content": content, "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
    except Exception:
        return None

def db_load_chat(uid, topic):
    try:
        res = db().table("chat_history").select("*").eq("user_id", uid)\
                  .eq("topic", topic).order("created_at").execute()
        return res.data or []
    except Exception:
        return []

def get_topic_subtopic_names(course_id, module_idx, topic_idx):
    course = COURSES.get(course_id)
    if not course or module_idx >= len(course["modules"]): return None, None
    module = course["modules"][module_idx]
    if topic_idx >= len(module["topics"]): return None, None
    return module["title"], module["topics"][topic_idx]["title"]

def db_save_progress(uid, topic, subtopic, status, score=None):
    try:
        payload = {
            "user_id": uid, "topic": topic, "subtopic": subtopic,
            "status": status, "score": score,
            "completed_at": datetime.now(timezone.utc).isoformat() if status == "completed" else None
        }
        return db().table("topic_progress").upsert(
            payload, on_conflict="user_id,topic,subtopic"
        ).execute()
    except Exception:
        return None

def db_get_progress(uid):
    try:
        res = db().table("topic_progress").select("*").eq("user_id", uid).execute()
        return res.data or []
    except Exception:
        return []

def db_get_progress_dict(uid):
    prog_list = db_get_progress(uid)
    return {
        f"{r['topic']}:{r['subtopic']}": {"status": r["status"], "score": r.get("score")}
        for r in prog_list
    }

def _sync_progress_from_db(uid):
    try:
        pdict = db_get_progress_dict(uid)
        st.session_state.progress = pdict
        return pdict
    except Exception:
        return st.session_state.get("progress", {})

def _save_and_sync_progress(uid, course_id, module_idx, topic_idx, status, score=None):
    topic, subtopic = get_topic_subtopic_names(course_id, module_idx, topic_idx)
    if not (topic and subtopic): return False
    if not db_save_progress(uid, topic, subtopic, status, score): return False
    _sync_progress_from_db(uid)
    return True

def course_progress_pct(uid, course_id):
    prog = st.session_state.get("progress")
    if prog is None:
        prog = db_get_progress_dict(uid)
    course = COURSES.get(course_id)
    if not course: return 0
    total = sum(len(m["topics"]) for m in course["modules"])
    if total == 0: return 0
    done = sum(
        1 for m in course["modules"]
        for t in m["topics"]
        if prog.get(f"{m['title']}:{t['title']}", {}).get("status") == "completed"
    )
    return round(done / total * 100)

def restore_user_session(uid):
    user = db_get_user_by_id(uid)
    if user:
        st.session_state.update(
            authenticated=True, user_id=uid,
            user_name=user["name"], user_username=user["username"]
        )
        _sync_progress_from_db(uid)
        return True
    return False

def db_save_mcq(uid, topic, question, selected, correct):
    try:
        return db().table("mcq_attempts").insert({
            "user_id": uid, "topic": topic, "question": question,
            "selected_answer": selected, "correct_answer": correct,
            "is_correct": selected == correct,
            "attempted_at": datetime.now(timezone.utc).isoformat()
        }).execute()
    except Exception:
        return None

def db_save_code(uid, topic, code, passed, feedback="", score=None):
    try:
        payload = {
            "user_id": uid, "topic": topic, "submitted_code": code,
            "test_passed": bool(passed), "feedback": feedback,
            "attempted_at": datetime.now(timezone.utc).isoformat()
        }
        if score is not None:
            payload["score"] = int(score)
        return db().table("code_attempts").insert(payload).execute()
    except Exception:
        return None

# ─── AUTHENTICATION ───────────────────────────────────────────────────
def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def auth_signup(username, password, name):
    if db_get_user(username): return None, "Username already exists"
    uid = str(uuid.uuid4())
    if db_create_user(uid, username, _hash(password), name):
        st.session_state.progress = {}
        return uid, None
    return None, "Could not create user"

def auth_login(username, password):
    user = db_get_user(username)
    if not user: return None, None, "User not found"
    if user["password_hash"] != _hash(password): return None, None, "Incorrect password"
    uid = user["id"]
    _sync_progress_from_db(uid)
    return uid, user["name"], None

# ─── SCORING ──────────────────────────────────────────────────────────
def _compute_mcq_score(correct, total): return round((correct / total) * 100) if total else 0
def _compute_code_score(passed, total): return round((passed / total) * 100) if total else 0
def _score_to_status(score): return "completed" if score >= 70 else "in_progress"

# ─── AI GENERATION ────────────────────────────────────────────────────
def get_topic_content(course_id, mod_idx, topic_idx):
    key = f"{course_id}:{mod_idx}:{topic_idx}"
    if key in st.session_state.topic_content_cache:
        return st.session_state.topic_content_cache[key]
    course = COURSES[course_id]
    module = course["modules"][mod_idx]
    topic  = module["topics"][topic_idx]["title"]
    system = (
        f"You are a world-class instructor teaching '{course['title']}'. "
        "Lessons: 1) Core concept (2-3 paragraphs) 2) Real-world application 3) Code/template "
        "4) Common mistakes 5) Key takeaways (3 bullets). Use markdown."
    )
    content = _call_llm(
        [{"role": "user", "content": f"Teach me: **{topic}**\nModule: {module['title']}"}],
        system=system, max_tokens=2000, temp=0.4
    )
    st.session_state.topic_content_cache[key] = content
    return content

def gen_mcq(course_id, mod_idx, topic_idx, n=5):
    course = COURSES[course_id]
    module = course["modules"][mod_idx]
    topic  = module["topics"][topic_idx]["title"]
    system = "You are a rigorous exam writer. Return ONLY a valid JSON array, no markdown fences."
    prompt = (
        f"Write {n} MCQ questions on: '{topic}'\nCourse: {course['title']} — {module['title']}\n"
        "Each question must test application or analysis. JSON format: "
        '[{"question":"...","options":{"A":"...","B":"...","C":"...","D":"..."},'
        '"correct":"B","explanation":"..."}]'
    )
    for _ in range(2):
        raw = _call_llm([{"role": "user", "content": prompt}], system=system, max_tokens=1500, temp=0.3)
        questions = _extract_json_array(raw)
        if isinstance(questions, list): return questions
    return []

# ─── CODE EXECUTION (kept for potential future use) ──────────────────
def _run_code(source: str) -> dict:
    ns = {}
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            exec(compile(source, "<student>", "exec"), ns)
        return {"ok": True, "stdout": stdout_buf.getvalue(), "stderr": stderr_buf.getvalue(),
                "traceback": "", "error_type": "", "error_msg": ""}
    except Exception as exc:
        full_tb = tb_module.format_exc()
        clean = [l for l in full_tb.splitlines()
                 if 'exec(compile' not in l and '_run_code' not in l]
        return {"ok": False, "stdout": stdout_buf.getvalue(), "stderr": stderr_buf.getvalue(),
                "traceback": "\n".join(clean), "error_type": type(exc).__name__, "error_msg": str(exc)}

def eval_code(task: dict, code: str) -> dict:
    if not code.strip():
        return {"ok": False, "stdout": "", "traceback": "",
                "interpretation": "No code submitted.",
                "fix": "Write your solution in the editor.", "correct": False}
    try:
        ast.parse(code)
    except SyntaxError:
        return {"ok": False, "stdout": "", "traceback": "⚠️ Syntax error detected.",
                "interpretation": "Code contains syntax errors.",
                "fix": "Fix the syntax error.", "correct": False}
    run = _run_code(code)
    actual_output = run["stdout"].strip()
    expected_output = task.get("expected_output", "").strip()
    correct = actual_output == expected_output
    if run["ok"]:
        interpretation = (f"✅ Correct! Output: {actual_output}" if correct
                          else f"Output: `{actual_output}` — Expected: `{expected_output}`")
        fix = "" if correct else "Adjust your logic to match the expected output."
    else:
        interpretation = "Runtime error."
        fix = "Fix the error and rerun."
    return {"ok": run["ok"], "stdout": run["stdout"],
            "traceback": run["traceback"] if not run["ok"] else "",
            "interpretation": interpretation, "fix": fix, "correct": correct}

# ─── UI HELPERS ───────────────────────────────────────────────────────
def _tag(text, color="var(--primary)"):
    return (
        f'<span style="display:inline-flex;align-items:center;'
        f'background:{color}18;color:{color};border:1px solid {color}30;'
        f'border-radius:4px;padding:1px 7px;font-size:0.65rem;font-weight:600;">{text}</span>'
    )

def _diff_badge(difficulty):
    colors = {"Beginner": "#16a34a", "Intermediate": "#d97706", "Advanced": "#dc2626", "Expert": "#7c3aed"}
    return _tag(difficulty, colors.get(difficulty, "var(--primary)"))

def _progress_bar_html(pct, height="4px"):
    return (
        f'<div style="background:var(--border);border-radius:50px;height:{height};overflow:hidden;">'
        f'<div style="width:{pct}%;height:100%;background:var(--primary);'
        f'transition:width 0.4s ease;border-radius:50px;"></div></div>'
    )

# ─── PAGE: AUTH ───────────────────────────────────────────────────────
def page_auth():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("""
        <div style="text-align:center; padding: 2rem 0 1rem;">
            <div style="font-size:2rem; color:var(--primary);">◈</div>
            <div style="font-size:1.8rem; font-weight:600; margin-bottom:0.5rem;
                        color:var(--text);">TEACHER.AI</div>
            <div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:1.5rem;">
                An Advanced learning system with Awareness
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not _supabase():
            st.error("🚨 Database not available. Configure Supabase environment variables.")
            st.stop()

        mode = st.radio("mode", ["Sign In", "Create Account"], horizontal=True, label_visibility="collapsed")
        with st.form("auth_form"):
            dname = ""
            if mode == "Create Account":
                dname = st.text_input("Full Name", placeholder="Ada Lovelace")
            uname = st.text_input("Username", placeholder="username")
            pwd   = st.text_input("Password", type="password", placeholder="••••••••")
            ok    = st.form_submit_button(
                "Create Account →" if mode == "Create Account" else "Sign In →",
                use_container_width=True, type="primary"
            )

        if ok:
            if not uname or not pwd:
                st.error("Fill in all fields.")
            elif mode == "Create Account":
                if not dname.strip():
                    st.error("Enter your name.")
                else:
                    with st.spinner("Creating account…"):
                        uid, err = auth_signup(uname.strip().lower(), pwd, dname.strip())
                        if err: st.error(err)
                        else:
                            st.session_state.update(
                                authenticated=True, user_id=uid,
                                user_username=uname.strip().lower(),
                                user_name=dname.strip()
                            )
                            st.rerun()
            else:
                with st.spinner("Signing in…"):
                    uid, nm, err = auth_login(uname.strip().lower(), pwd)
                    if err: st.error(err)
                    else:
                        st.session_state.update(
                            authenticated=True, user_id=uid,
                            user_username=uname.strip().lower(),
                            user_name=nm or uname
                        )
                        st.rerun()

# ─── PAGE: CATALOG ────────────────────────────────────────────────────
def page_catalog():
    uid  = st.session_state.user_id
    name = st.session_state.user_name or "there"

    st.markdown(f"""
    <div style="padding:2rem 0 1rem; border-bottom:1px solid var(--border); margin-bottom:1.5rem;">
        <div style="font-size:0.7rem; color:var(--primary); text-transform:uppercase;
                    letter-spacing:0.1em;">Welcome back, {name}</div>
        <div style="font-size:2.8rem; font-weight:500; line-height:1.1; margin-bottom:6px;
                    color:var(--text);">Your Learning<br>
            <em style="color:var(--primary);">Curriculum</em></div>
        <div style="font-size:0.85rem; color:var(--text-muted); max-width:520px;">
            An Advanced learning system with Awareness
        </div>
    </div>
    """, unsafe_allow_html=True)

    courses_items = list(COURSES.items())
    for i in range(0, len(courses_items), 2):
        row = courses_items[i:i+2]
        cols = st.columns(len(row), gap="medium")
        for col, (cid, c) in zip(cols, row):
            pct = course_progress_pct(uid, cid)
            total_topics = sum(len(m["topics"]) for m in c["modules"])
            with col:
                st.markdown(f"""
                <div style="background:var(--card); border-radius:20px;
                            padding:1rem 1rem 0.8rem; border:1px solid var(--border);
                            position:relative; overflow:hidden; margin-bottom:4px;
                            box-shadow:var(--shadow);">
                    <div style="position:absolute;top:0;left:0;right:0;
                                height:3px;background:var(--primary);"></div>
                    <div style="font-size:1rem; font-weight:600;
                                color:var(--text);">{c['title']}</div>
                    <div style="font-size:0.7rem; color:var(--text-muted);
                                margin-bottom:0.6rem;">{c['tagline']}</div>
                    <div style="display:flex; gap:10px; margin-bottom:0.6rem;
                                font-size:0.65rem; color:var(--text-muted);">
                        <div><strong>{len(c['modules'])}</strong> modules</div>
                        <div><strong>{total_topics}</strong> topics</div>
                        <div><strong>{c['hours']}h</strong></div>
                    </div>
                    <div style="display:flex;justify-content:space-between;
                                font-size:0.6rem;color:var(--text-muted);margin-bottom:4px;">
                        <span>Progress</span>
                        <span style="color:var(--primary);font-weight:600;">{pct}%</span>
                    </div>
                    {_progress_bar_html(pct)}
                </div>
                """, unsafe_allow_html=True)
                label = "Continue →" if pct > 0 else "Start Course →"
                if st.button(label, key=f"cat_{cid}", use_container_width=True,
                             type="primary" if pct > 0 else "secondary"):
                    st.session_state.update(
                        active_course=cid, page="course",
                        active_module_idx=0, active_topic_idx=0,
                        active_mode="lesson",
                        mcq_questions=[], mcq_answers={},
                        mcq_submitted=False, mcq_results=None,
                        selected_task=None, code_eval=None,
                        code_submitted=False, user_code=""
                    )
                    st.rerun()

# ─── COURSE SIDEBAR (with sign‑out at bottom) ───────────────────────
def render_course_sidebar():
    uid = st.session_state.user_id
    cid = st.session_state.active_course

    with st.sidebar:
        st.markdown(f"""
        <div style="padding:0.8rem 0 0.6rem;">
            <div style="font-weight:600; font-size:0.85rem; color:var(--text);">
                {st.session_state.user_name}</div>
            <div style="color:var(--text-muted); font-size:0.65rem;">
                TEACHER.AI</div>
        </div>
        """, unsafe_allow_html=True)

        if cid and cid in COURSES:
            course = COURSES[cid]
            st.markdown(f"""
            <div style="padding:0.4rem 0 0.6rem; border-top:1px solid var(--border);">
                <div style="font-weight:600; font-size:0.8rem; color:var(--text);">
                    {course['title']}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("← All Courses", use_container_width=True, key="sb_all"):
                st.session_state.update(active_course=None, page="catalog")
                st.rerun()
            if st.button("◈ Dashboard", use_container_width=True, key="sb_dash"):
                st.session_state.page = "dashboard"
                st.rerun()

            st.divider()
            pct = course_progress_pct(uid, cid)
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between;
                            font-size:0.65rem; color:var(--text-muted);">
                    <span>Course progress</span>
                    <span style="color:var(--primary); font-weight:600;">{pct}%</span>
                </div>
                {_progress_bar_html(pct, "3px")}
            </div>
            """, unsafe_allow_html=True)

            prog  = db_get_progress_dict(uid)
            cur_m = st.session_state.active_module_idx
            cur_t = st.session_state.active_topic_idx

            for m_i, module in enumerate(course["modules"]):
                done_m  = sum(1 for t in module["topics"]
                              if prog.get(f"{module['title']}:{t['title']}", {}).get("status") == "completed")
                total_m = len(module["topics"])
                active_m = (m_i == cur_m)
                st.markdown(f"""
                <div style="background:{'rgba(220,38,38,0.04)' if active_m else 'transparent'};
                            border-radius:8px; padding:5px 7px; margin-bottom:2px;
                            border:1px solid {'var(--primary)44' if active_m else 'transparent'};">
                    <div style="font-size:0.67rem; font-weight:600;
                                color:{'var(--primary)' if active_m else 'var(--text-light)'};
                                margin-bottom:2px;">{module['title'][:38]}</div>
                    <div style="font-size:0.6rem; color:var(--text-muted);">{done_m}/{total_m} done</div>
                </div>
                """, unsafe_allow_html=True)
                if active_m:
                    for t_i, topic in enumerate(module["topics"]):
                        key    = f"{module['title']}:{topic['title']}"
                        done   = prog.get(key, {}).get("status") == "completed"
                        active_t = (t_i == cur_t)
                        icon_c = "✓" if done else ("▶" if active_t else "·")
                        col    = "var(--primary)" if done or active_t else "var(--text-muted)"
                        st.markdown(f"""
                        <div style="padding:3px 6px 3px 12px;">
                            <div style="display:flex; gap:6px; align-items:flex-start;">
                                <span style="color:{col}; font-size:0.62rem;">{icon_c}</span>
                                <div style="font-size:0.71rem; color:{col};
                                            line-height:1.35;">{topic['title'][:50]}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("Go", key=f"nav_{cid}_{m_i}_{t_i}", use_container_width=True):
                            st.session_state.update(
                                active_module_idx=m_i, active_topic_idx=t_i,
                                active_mode="lesson",
                                mcq_questions=[], mcq_answers={},
                                mcq_submitted=False, mcq_results=None,
                                selected_task=None, code_eval=None,
                                code_submitted=False, user_code=""
                            )
                            st.rerun()

        st.sidebar.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
        if st.sidebar.button("⊗ Sign Out", use_container_width=True, key="sidebar_signout"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            for k2, v2 in _DEFAULTS.items():
                st.session_state[k2] = v2
            st.rerun()

# ─── COURSE: LESSON / QUIZ ──────────────────────────────────────────
def _advance_topic():
    cid = st.session_state.active_course
    if not cid: return
    course = COURSES.get(cid)
    if not course: return
    cur_m = st.session_state.active_module_idx
    cur_t = st.session_state.active_topic_idx
    if cur_t + 1 < len(course["modules"][cur_m]["topics"]):
        st.session_state.active_topic_idx += 1
    elif cur_m + 1 < len(course["modules"]):
        st.session_state.active_module_idx += 1
        st.session_state.active_topic_idx  = 0
    st.session_state.update(
        active_mode="lesson",
        mcq_questions=[], mcq_answers={}, mcq_submitted=False, mcq_results=None,
        selected_task=None, user_code="", code_eval=None, code_submitted=False
    )

def render_lesson(course, module, topic):
    content = get_topic_content(
        st.session_state.active_course,
        st.session_state.active_module_idx,
        st.session_state.active_topic_idx
    )
    st.markdown(content or "*Loading lesson...*")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Mark as Completed", use_container_width=True, type="primary"):
            _save_and_sync_progress(
                st.session_state.user_id, st.session_state.active_course,
                st.session_state.active_module_idx, st.session_state.active_topic_idx,
                "completed", score=100
            )
            st.success("Great job! Moving to next topic.")
            _advance_topic()
            st.rerun()
    with c2:
        if st.button("⏭ Skip for now", use_container_width=True):
            _advance_topic()
            st.rerun()

def render_quiz(course, module, topic):
    if not st.session_state.mcq_questions:
        with st.spinner("Generating questions..."):
            st.session_state.mcq_questions = gen_mcq(
                st.session_state.active_course,
                st.session_state.active_module_idx,
                st.session_state.active_topic_idx,
                n=5
            )
    questions = st.session_state.mcq_questions
    if not questions:
        st.warning("Could not generate questions.")
        if st.button("Retry"):
            st.session_state.mcq_questions = []
            st.rerun()
        return

    st.subheader("📝 Knowledge Check")
    user_answers = {}
    for i, q in enumerate(questions):
        opts = q.get("options", {})
        if not opts: continue
        user_choice = st.radio(
            f"**{i+1}. {q.get('question', '')}**",
            list(opts.keys()),
            format_func=lambda x, o=opts: f"{x}: {o[x]}",
            key=f"mcq_{i}", index=None
        )
        user_answers[i] = user_choice

    if st.button("Submit Answers", type="primary", use_container_width=True):
        correct_count = 0
        results = []
        for i, q in enumerate(questions):
            correct  = q.get("correct", "")
            selected = user_answers.get(i)
            is_ok    = (selected == correct)
            if is_ok: correct_count += 1
            results.append({"question": q.get("question", ""), "selected": selected,
                             "correct": correct, "is_correct": is_ok,
                             "explanation": q.get("explanation", "")})
            db_save_mcq(st.session_state.user_id, topic["title"],
                        q.get("question", ""), selected or "", correct)
        score = _compute_mcq_score(correct_count, len(questions))
        st.session_state.mcq_results  = {"results": results, "score": score}
        st.session_state.mcq_submitted = True
        _save_and_sync_progress(
            st.session_state.user_id, st.session_state.active_course,
            st.session_state.active_module_idx, st.session_state.active_topic_idx,
            _score_to_status(score), score
        )
        st.rerun()

    if st.session_state.mcq_submitted and st.session_state.mcq_results:
        r = st.session_state.mcq_results
        st.success(f"Your score: {r['score']}%")
        for res in r["results"]:
            icon = "✅" if res["is_correct"] else "❌"
            st.markdown(f"{icon} **{res['question']}**")
            st.caption(f"Your: {res['selected']} | Correct: {res['correct']}")
            if res["explanation"]:
                st.caption(f"💡 {res['explanation']}")
        if st.button("Next Topic →", use_container_width=True):
            _advance_topic()
            st.rerun()

def page_course():
    cid = st.session_state.active_course
    if not cid: return st.error("No course selected.")
    course = COURSES.get(cid)
    if not course: return st.error("Course not found.")
    module = course["modules"][st.session_state.active_module_idx]
    topic  = module["topics"][st.session_state.active_topic_idx]

    st.markdown(f"""
    <div style="margin-bottom:1rem;">
        <div style="font-size:0.7rem; color:var(--primary);">
            {course['title']} / {module['title']}</div>
        <div style="font-size:1.4rem; font-weight:600;
                    color:var(--text);">{topic['title']}</div>
    </div>
    """, unsafe_allow_html=True)

    mode = st.session_state.active_mode or "lesson"
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📖 Lesson", use_container_width=True,
                     type="primary" if mode == "lesson" else "secondary"):
            st.session_state.active_mode = "lesson"; st.rerun()
    with col2:
        if st.button("📝 Quiz", use_container_width=True,
                     type="primary" if mode == "quiz" else "secondary"):
            st.session_state.active_mode = "quiz"; st.rerun()

    st.divider()

    if mode == "lesson":
        render_lesson(course, module, topic)
    elif mode == "quiz":
        render_quiz(course, module, topic)

# ─── PAGE: DASHBOARD ─────────────────────────────────────────────────
def page_dashboard():
    uid  = st.session_state.user_id
    name = st.session_state.user_name or "there"

    prog = _sync_progress_from_db(uid)

    all_topics = [
        (course_id, m["title"], t["title"])
        for course_id, course in COURSES.items()
        for m in course["modules"]
        for t in m["topics"]
    ]
    total_topics  = len(all_topics)
    completed_set = {
        f"{cid}:{mt}:{tt}"
        for cid, mt, tt in all_topics
        if prog.get(f"{mt}:{tt}", {}).get("status") == "completed"
    }
    completed     = len(completed_set)
    in_progress   = sum(
        1 for v in prog.values() if v.get("status") == "in_progress"
    )

    overall_pct   = round(completed / total_topics * 100) if total_topics else 0
    avg_score_vals = [v["score"] for v in prog.values()
                      if v.get("score") is not None and isinstance(v["score"], (int, float))]
    avg_score      = round(sum(avg_score_vals) / len(avg_score_vals)) if avg_score_vals else 0

    st.markdown(f"""
    <div style="padding:1.5rem 0 1rem; border-bottom:1px solid var(--border);
                margin-bottom:1.5rem;">
        <div style="font-size:0.7rem; color:var(--primary); text-transform:uppercase;
                    letter-spacing:0.1em; margin-bottom:4px;">Learning Dashboard</div>
        <div style="font-size:2rem; font-weight:600; color:var(--text);
                    line-height:1.2;">{name}'s Progress</div>
        <div style="font-size:0.85rem; color:var(--text-muted); margin-top:4px;">
            All your stats across the 2026 curriculum.
        </div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Topics Completed", completed,
                  delta=f"{overall_pct}% of curriculum")
    with m2:
        st.metric("In Progress", in_progress)
    with m3:
        st.metric("Courses Enrolled", len(COURSES))
    with m4:
        st.metric("Avg Quiz Score", f"{avg_score}%" if avg_score_vals else "—")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:var(--card); border:1px solid var(--border);
                border-radius:16px; padding:1.2rem 1.4rem; margin-bottom:1.2rem;
                box-shadow:var(--shadow);">
        <div style="display:flex; justify-content:space-between; align-items:center;
                    margin-bottom:10px;">
            <div style="font-size:0.85rem; font-weight:600;
                        color:var(--text);">Overall curriculum progress</div>
            <div style="font-size:1.2rem; font-weight:700;
                        color:var(--primary);">{overall_pct}%</div>
        </div>
        {_progress_bar_html(overall_pct, "10px")}
        <div style="font-size:0.72rem; color:var(--text-muted); margin-top:8px;">
            {completed} of {total_topics} topics completed across {len(COURSES)} courses
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.75rem; font-weight:600; color:var(--text-muted);
                text-transform:uppercase; letter-spacing:0.08em;
                margin-bottom:0.8rem;">Course Breakdown</div>
    """, unsafe_allow_html=True)

    course_cols = st.columns(2)
    for idx, (cid, course) in enumerate(COURSES.items()):
        pct         = course_progress_pct(uid, cid)
        total_c     = sum(len(m["topics"]) for m in course["modules"])
        done_c      = round(pct / 100 * total_c)
        status_html = ""
        if pct == 100:
            status_html = (
                f'<span style="background:var(--success-bg);color:var(--success);'
                f'border:1px solid #bbf7d0;border-radius:20px;padding:2px 10px;'
                f'font-size:0.6rem;font-weight:600;">Completed</span>'
            )
        elif pct > 0:
            status_html = (
                f'<span style="background:var(--warning-bg);color:var(--warning);'
                f'border:1px solid #fde68a;border-radius:20px;padding:2px 10px;'
                f'font-size:0.6rem;font-weight:600;">In Progress</span>'
            )
        else:
            status_html = (
                f'<span style="background:var(--bg-offset);color:var(--text-muted);'
                f'border:1px solid var(--border2);border-radius:20px;padding:2px 10px;'
                f'font-size:0.6rem;font-weight:600;">Not Started</span>'
            )

        with course_cols[idx % 2]:
            st.markdown(f"""
            <div style="background:var(--card); border:1px solid var(--border);
                        border-radius:16px; padding:1rem 1.2rem; margin-bottom:0.8rem;
                        box-shadow:var(--shadow);">
                <div style="display:flex; justify-content:space-between;
                            align-items:flex-start; margin-bottom:8px;">
                    <div>
                        <div style="font-size:0.88rem; font-weight:600;
                                    color:var(--text);">{course['title']}</div>
                        <div style="font-size:0.65rem;
                                    color:var(--text-muted);">{course['difficulty']} · {course['hours']}h</div>
                    </div>
                    {status_html}
                </div>
                <div style="display:flex; justify-content:space-between;
                            font-size:0.65rem; color:var(--text-muted); margin-bottom:6px;">
                    <span>{done_c} / {total_c} topics</span>
                    <span style="color:var(--primary); font-weight:600;">{pct}%</span>
                </div>
                {_progress_bar_html(pct, "6px")}
            </div>
            """, unsafe_allow_html=True)

            btn_label = ("View Course →" if pct == 100
                         else "Continue →" if pct > 0 else "Start →")
            if st.button(btn_label, key=f"dash_go_{cid}", use_container_width=True,
                         type="primary" if pct > 0 else "secondary"):
                st.session_state.update(
                    active_course=cid, page="course",
                    active_module_idx=0, active_topic_idx=0,
                    active_mode="lesson",
                    mcq_questions=[], mcq_answers={},
                    mcq_submitted=False, mcq_results=None,
                    selected_task=None, code_eval=None,
                    code_submitted=False, user_code=""
                )
                st.rerun()

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    b1, b2, _ = st.columns([1, 1, 4])
    with b1:
        if st.button("← Catalog", use_container_width=True):
            st.session_state.page = "catalog"; st.rerun()

# ─── PERSONAL TEACHER BAR ────────────────────────────────────────────
def render_personal_teacher_bar():
    uid = st.session_state.user_id
    if not uid: return

    if not st.session_state.guide_messages_loaded:
        st.session_state.guide_messages        = db_load_guide_messages(uid)
        st.session_state.guide_messages_loaded = True

    st.markdown("""
    <div style="background:var(--bg-offset); border:1px solid var(--border);
                border-radius:20px; padding:1rem 1.4rem 0.5rem;
                margin-top:2rem; box-shadow:var(--shadow);">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
            <span style="font-size:1rem; color:var(--primary);">🧑‍🏫</span>
            <span style="font-size:0.9rem; font-weight:600;
                         color:var(--text);">Personal Teacher</span>
            <span style="font-size:0.72rem; color:var(--text-muted);">
                — ask me anything about your courses</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.guide_messages:
        with st.expander("Conversation history", expanded=False):
            for msg in st.session_state.guide_messages[-6:]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

    query = st.chat_input("Ask your Personal Teacher…", key="personal_teacher_input")
    if query:
        st.session_state.guide_messages.append({"role": "user", "content": query})
        db_save_guide_message(uid, "user", query)

        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            system_prompt = (
                "You are TEACHER.AI's Personal Teacher, a warm, knowledgeable assistant "
                "for career, learning, and productivity. Be concise and encouraging."
            )
            msgs = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.guide_messages[-8:]
            ]
            response = st.write_stream(_stream_llm(msgs, system_prompt, max_tokens=800))

        st.session_state.guide_messages.append({"role": "assistant", "content": response})
        db_save_guide_message(uid, "assistant", response)
        st.rerun()

    if st.button("🗑 Clear history", key="clear_teacher", use_container_width=False):
        try:
            db().table("personal_guide").delete().eq("user_id", uid).execute()
        except Exception:
            pass
        st.session_state.guide_messages        = []
        st.session_state.guide_messages_loaded = True
        st.rerun()

# ─── MAIN ROUTER ──────────────────────────────────────────────────────
def main():
    if st.session_state.user_id and not st.session_state.authenticated:
        restore_user_session(st.session_state.user_id)
    if not st.session_state.authenticated:
        page_auth()
        return

    uid = st.session_state.user_id
    if uid and st.session_state.progress is None:
        _sync_progress_from_db(uid)

    render_course_sidebar()

    p = st.session_state.page
    if p == "catalog":
        page_catalog()
    elif p == "course":
        page_course()
    elif p == "dashboard":
        page_dashboard()
    else:
        st.session_state.page = "catalog"
        st.rerun()

    render_personal_teacher_bar()

if __name__ == "__main__":
    main()