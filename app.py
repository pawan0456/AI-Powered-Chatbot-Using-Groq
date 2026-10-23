import streamlit as st
import os

# Load .env file for local development (no effect on Render —
# Render injects env vars directly, dotenv is just a no-op there)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from groq import Groq
from tavily import TavilyClient
import html, json, time, re, base64
from datetime import datetime
from PIL import Image
from io import BytesIO

# ╔══════════════════════════════════════════════════════════════════╗
# ║                     API KEYS  (edit here)                       ║
# ╚══════════════════════════════════════════════════════════════════╝
GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(page_title="SmartChat AI", page_icon="✦", layout="wide")

# ══════════════════════════════════════════════════════════════════
#  FULL CSS  — glassmorphism dark theme
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }

/* ── Root background: deep space ── */
.stApp {
    background: #050508;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(124,58,237,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(56,189,248,0.08) 0%, transparent 50%),
        radial-gradient(ellipse 50% 50% at 50% 50%, rgba(16,16,30,1) 0%, transparent 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: rgba(8,8,16,0.95) !important;
    border-right: 1px solid rgba(124,58,237,0.2) !important;
    backdrop-filter: blur(20px);
}
section[data-testid="stSidebar"] > div { padding-top: 1rem; }

/* ── Sidebar logo ── */
.sb-logo {
    display: flex; align-items: center; gap: 10px;
    padding: 0.5rem 0 1.2rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1rem;
}
.sb-logo-icon {
    width: 36px; height: 36px; border-radius: 10px;
    background: linear-gradient(135deg, #7c3aed, #3b82f6);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0;
}
.sb-logo-text { font-size: 1.1rem; font-weight: 700; color: #fff; letter-spacing: -0.02em; }
.sb-logo-sub  { font-size: 0.68rem; color: #6b7280; margin-top: 1px; }

/* ── Sidebar sections ── */
.sb-sec {
    font-size: 0.65rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #4b5563;
    padding: 0.9rem 0 0.35rem;
}

/* ── Stat cards ── */
.stat-row { display: flex; gap: 6px; margin: 4px 0 8px; }
.stat-card {
    flex: 1; background: rgba(124,58,237,0.08);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 10px; padding: 7px 8px; text-align: center;
}
.stat-card .sv { font-size: 1rem; font-weight: 700; color: #a78bfa; display: block; }
.stat-card .sl { font-size: 0.62rem; color: #6b7280; }

/* ── Persona grid ── */
.persona-active {
    background: rgba(124,58,237,0.25) !important;
    border-color: #7c3aed !important;
    color: #c4b5fd !important;
}

/* ── Main header ── */
.main-header {
    text-align: center;
    padding: 2.5rem 0 1rem;
    position: relative;
}
.main-header::before {
    content: '';
    position: absolute; top: 0; left: 50%; transform: translateX(-50%);
    width: 200px; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(124,58,237,0.6), transparent);
}
.main-title {
    font-size: 2.8rem; font-weight: 700; letter-spacing: -0.04em;
    background: linear-gradient(135deg, #c4b5fd 0%, #818cf8 40%, #38bdf8 80%, #34d399 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1.1;
}
.main-sub {
    color: #4b5563; font-size: 0.85rem; margin-top: 0.5rem;
    letter-spacing: 0.02em;
}
.status-dot {
    display: inline-block; width: 6px; height: 6px;
    border-radius: 50%; background: #34d399;
    margin-right: 6px; vertical-align: middle;
    box-shadow: 0 0 6px #34d399;
}

/* ── Welcome cards ── */
.welcome-wrap { max-width: 600px; margin: 2rem auto 0; }
.welcome-title { text-align: center; color: #374151; font-size: 0.85rem; margin-bottom: 1rem; }
.wcard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.wcard {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 14px 16px;
    cursor: pointer; transition: all 0.2s;
}
.wcard:hover {
    background: rgba(124,58,237,0.1);
    border-color: rgba(124,58,237,0.4);
    transform: translateY(-1px);
}
.wcard-icon { font-size: 1.4rem; margin-bottom: 6px; }
.wcard-title { font-size: 0.85rem; font-weight: 600; color: #e2e8f0; }
.wcard-sub   { font-size: 0.72rem; color: #4b5563; margin-top: 2px; }

/* ── Chat container ── */
.chat-area { max-width: 820px; margin: 0 auto; padding: 0 1rem; }

/* ── User bubble ── */
.bubble-wrap-user { display: flex; justify-content: flex-end; margin: 0.6rem 0; }
.bubble-user {
    background: linear-gradient(135deg, #6d28d9 0%, #4f46e5 100%);
    color: #fff;
    padding: 0.8rem 1.15rem;
    border-radius: 20px 20px 4px 20px;
    max-width: 75%;
    font-size: 0.93rem; line-height: 1.65;
    box-shadow: 0 4px 20px rgba(109,40,217,0.3);
    word-break: break-word;
}
.bubble-meta-user {
    text-align: right;
    font-size: 0.65rem; color: #374151;
    margin: 2px 4px 8px;
}

/* ── Bot bubble ── */
.bubble-wrap-bot { display: flex; justify-content: flex-start; margin: 0.6rem 0; gap: 10px; align-items: flex-start; }
.bot-avatar {
    width: 32px; height: 32px; border-radius: 10px; flex-shrink: 0;
    background: linear-gradient(135deg, #7c3aed, #3b82f6);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem; margin-top: 2px;
}
.bubble-bot {
    background: rgba(22,22,35,0.9);
    border: 1px solid rgba(255,255,255,0.07);
    color: #e2e8f0;
    padding: 0.85rem 1.15rem;
    border-radius: 4px 20px 20px 20px;
    max-width: 80%;
    font-size: 0.93rem; line-height: 1.7;
    backdrop-filter: blur(10px);
    word-break: break-word;
}
.bubble-bot code {
    background: rgba(124,58,237,0.15);
    color: #c4b5fd;
    padding: 1px 6px; border-radius: 4px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.84em;
}
.bubble-bot pre {
    background: rgba(0,0,0,0.5);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 10px; padding: 1rem;
    overflow-x: auto; margin: 0.6rem 0;
}
.bubble-bot pre code { background: transparent; padding: 0; font-size: 0.85rem; }
.bubble-bot h1, .bubble-bot h2, .bubble-bot h3 { color: #c4b5fd; margin: 0.8rem 0 0.4rem; }
.bubble-bot ul, .bubble-bot ol { padding-left: 1.2rem; margin: 0.4rem 0; }
.bubble-bot li { margin: 0.25rem 0; }
.bubble-bot p { margin: 0.4rem 0; }
.bubble-bot strong { color: #f1f5f9; }
.bubble-meta-bot { font-size: 0.65rem; color: #374151; margin: 2px 4px 6px 42px; }

/* ── Badges ── */
.badges { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 8px; }
.badge {
    font-size: 0.65rem; font-weight: 600; padding: 2px 8px;
    border-radius: 20px; letter-spacing: 0.03em;
}
.badge-web   { background: rgba(20,83,45,0.5);  color: #86efac; border: 1px solid rgba(134,239,172,0.2); }
.badge-model { background: rgba(30,27,75,0.5);  color: #a5b4fc; border: 1px solid rgba(165,180,252,0.2); }
.badge-pdf   { background: rgba(124,45,18,0.5); color: #fb923c; border: 1px solid rgba(251,146,60,0.2); }
.badge-img   { background: rgba(6,78,59,0.5);   color: #6ee7b7; border: 1px solid rgba(110,231,183,0.2); }
.badge-persona { background: rgba(69,26,3,0.5); color: #fcd34d; border: 1px solid rgba(252,211,77,0.2); }

/* ── Attachment preview ── */
.attach-preview {
    background: rgba(124,58,237,0.08);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 10px; padding: 8px 12px;
    font-size: 0.78rem; color: #a78bfa;
    margin-bottom: 8px; display: inline-flex;
    align-items: center; gap: 6px;
}

/* ── Follow-up chips ── */
.fu-wrap { max-width: 820px; margin: 0 auto 0.5rem; padding: 0 1rem; }
.fu-label { font-size: 0.72rem; color: #4b5563; margin-bottom: 6px; }
.fu-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.fu-chip {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    color: #94a3b8; font-size: 0.78rem;
    padding: 5px 14px; border-radius: 20px; cursor: pointer;
    transition: all 0.15s;
}
.fu-chip:hover { border-color: #7c3aed; color: #c4b5fd; background: rgba(124,58,237,0.1); }

/* ── Upload area ── */
.upload-strip {
    max-width: 820px; margin: 0 auto;
    padding: 0 1rem 0.5rem;
    display: flex; gap: 10px; align-items: center;
}

/* ── Divider ── */
.chat-divider { border: none; border-top: 1px solid rgba(255,255,255,0.04); margin: 0.5rem 0; max-width: 820px; margin: 0.5rem auto; }

/* ── Input area override ── */
.stChatInputContainer {
    max-width: 820px !important;
    margin: 0 auto !important;
}
[data-testid="stChatInput"] > div {
    background: rgba(22,22,35,0.9) !important;
    border: 1px solid rgba(124,58,237,0.3) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(10px);
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: rgba(124,58,237,0.7) !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.1) !important;
}

/* ── Streamlit overrides ── */
#MainMenu, footer, .stDeployButton { visibility: hidden; display: none; }
.block-container { padding-top: 0 !important; padding-bottom: 2rem !important; }
div[data-testid="column"] { padding: 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.3); border-radius: 4px; }

/* ── Streamlit button overrides ── */
.stButton > button {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #94a3b8 !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.82rem !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: rgba(124,58,237,0.15) !important;
    border-color: rgba(124,58,237,0.4) !important;
    color: #c4b5fd !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(124,58,237,0.4), rgba(79,70,229,0.4)) !important;
    border-color: rgba(124,58,237,0.5) !important;
    color: #c4b5fd !important;
}

/* ── Select / slider ── */
.stSelectbox > div > div {
    background: rgba(22,22,35,0.8) !important;
    border-color: rgba(124,58,237,0.25) !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
}
.stSlider > div > div { color: #a78bfa !important; }
[data-baseweb="slider"] div[role="slider"] { background: #7c3aed !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(22,22,35,0.5) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
    color: #94a3b8 !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(22,22,35,0.5) !important;
    border: 1px dashed rgba(124,58,237,0.3) !important;
    border-radius: 12px !important;
}

/* ── Toggle ── */
.stToggle > label { color: #94a3b8 !important; }

/* ── Warning / error ── */
.stAlert { border-radius: 12px !important; border: none !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════
PERSONAS = {
    "default":  {"icon": "✦",  "name": "Assistant", "prompt": "You are SmartChat, a brilliant and concise AI assistant. Answer clearly and accurately. Format with markdown when helpful."},
    "tutor":    {"icon": "📚", "name": "Tutor",     "prompt": "You are a patient teacher. Explain step by step with examples, analogies, and check understanding."},
    "coder":    {"icon": "💻", "name": "Coder",     "prompt": "You are a senior software engineer. Write clean, commented code. Explain your approach. Prefer Python unless specified."},
    "writer":   {"icon": "✍️", "name": "Writer",   "prompt": "You are a creative writing expert. Help craft compelling content with vivid, engaging language."},
    "analyst":  {"icon": "📊", "name": "Analyst",  "prompt": "You are a sharp analyst. Give structured insights, pros/cons, bullet points, and data-driven conclusions."},
    "chef":     {"icon": "🍳", "name": "Chef",     "prompt": "You are a world-class chef. Give recipes with exact measurements, substitutions, and pro tips."},
    "comedian": {"icon": "😄", "name": "Comedian", "prompt": "You are a witty comedian-assistant. Be genuinely helpful but sprinkle in clever humor and wordplay."},
    "doctor":   {"icon": "🩺", "name": "Dr. Info", "prompt": "You provide factual health information. Always remind users to consult a real doctor for personal medical advice."},
}

MODELS = {
    "llama-3.3-70b-versatile":  "LLaMA 3.3 70B  ★ Best",
    "llama-3.1-8b-instant":     "LLaMA 3.1 8B  ⚡ Fast",
    "qwen/qwen3.8-27b":         "Qwen 3 27B",
    "mixtral-8x7b-32768":       "Mixtral 8x7B",
}

STARTERS = [
    ("💡", "Explain quantum computing simply",      "Science concept"),
    ("🐍", "Write a Python web scraper",            "Code generation"),
    ("📰", "Latest AI news today",                  "Web search"),
    ("🍕", "Perfect pizza dough recipe",            "Cooking"),
    ("📊", "Analyze pros & cons of remote work",    "Analysis"),
    ("✍️", "Write a short story about the ocean",  "Creative writing"),
]

# ══════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════
def init_state():
    D = {
        "sessions":       {"New Chat": []},
        "active":         "New Chat",
        "sess_count":     1,
        "total_tokens":   0,
        "feedback":       {},
        "followups":      [],
        "persona":        "default",
        "custom_sys":     "",
        "model":          "llama-3.3-70b-versatile",
        "temperature":    0.7,
        "web_search":     True,
        "show_followups": True,
    }
    for k, v in D.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def msgs():  return st.session_state.sessions[st.session_state.active]
def set_msgs(m): st.session_state.sessions[st.session_state.active] = m

# ══════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════
def esc(t): return html.escape(str(t))

def extract_pdf_text(uploaded_file) -> str:
    """Extract text from PDF using PyMuPDF."""
    try:
        import fitz
        uploaded_file.seek(0)  # ★ always rewind before reading
        data = uploaded_file.read()
        if not data:
            return "[PDF extraction error: file stream was empty — try re-uploading]"
        doc  = fitz.open(stream=data, filetype="pdf")
        pages = []
        for i, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                pages.append(f"[Page {i+1}]\n{text.strip()}")
        doc.close()
        full = "\n\n".join(pages)
        return full[:12000]  # cap to avoid context overflow
    except Exception as e:
        return f"[PDF extraction error: {e}]"

def image_to_base64(uploaded_file):
    """Convert uploaded image to base64 for vision models."""
    uploaded_file.seek(0)  # ★ always rewind — prior reads (e.g. st.image preview) move the pointer
    data = uploaded_file.read()
    if not data:
        return "", ""
    b64    = base64.b64encode(data).decode("utf-8")
    suffix = uploaded_file.name.split(".")[-1].lower()
    mime   = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
              "png": "image/png",  "webp": "image/webp",
              "gif": "image/gif"}.get(suffix, "image/jpeg")
    return b64, mime

def do_web_search(query: str):
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        result = client.search(query=query, max_results=4)
        snippets, sources = [], []
        for r in result.get("results", []):
            snippets.append(f"• {r.get('title','')}: {r.get('content','')[:350]}")
            sources.append({"title": r.get("title",""), "url": r.get("url","")})
        return "\n".join(snippets) or "No results.", sources
    except Exception as e:
        return f"Search error: {e}", []

def needs_search(msg: str) -> bool:
    kw = ["latest","today","now","current","news","price","weather","score",
          "who is","what is","when did","recently","2024","2025","2026",
          "update","live","trending","stock","market","happened","breaking"]
    return any(k in msg.lower() for k in kw)

def get_followups(history: list, client) -> list:
    try:
        ctx = "\n".join([
            f"{str(m.get('role',''))}: {str(m.get('content',''))[:150]}"
            for m in (history[-4:] if isinstance(history, list) else [])
        ])
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": (
                f"Based on this conversation:\n{ctx}\n\n"
                "List exactly 3 follow-up questions as a JSON array.\n"
                "FORMAT: [\"question 1\", \"question 2\", \"question 3\"]\n"
                "Rules: plain strings only, no nested objects, no extra text."
            )}],
            max_tokens=200, temperature=0.6,
        )
        raw = r.choices[0].message.content or ""
        raw = re.sub(r"```[a-z]*", "", raw).strip()
        # Extract JSON array from response
        match = re.search(r'\[.*?\]', raw, re.DOTALL)
        if not match:
            return []
        parsed = json.loads(match.group())
        result = []
        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, str):
                    s = item.strip()
                    if s:
                        result.append(s)
                elif isinstance(item, (list, tuple)) and item:
                    result.append(str(item[0]).strip())
                elif isinstance(item, dict) and item:
                    result.append(str(next(iter(item.values()))).strip())
        return [q for q in result if isinstance(q, str) and len(q) > 3][:3]
    except Exception:
        return []

def auto_title(first_msg: str, client) -> str:
    try:
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content":f"3-4 word chat title, no punctuation: {first_msg[:200]}"}],
            max_tokens=15, temperature=0.5,
        )
        return r.choices[0].message.content.strip()[:35]
    except:
        return st.session_state.active

def export_md() -> str:
    lines = [f"# SmartChat — {st.session_state.active}\n",
             f"*{datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n"]
    for m in msgs():
        role = "**You**" if m["role"]=="user" else "**SmartChat**"
        lines.append(f"{role}: {m['content']}\n\n")
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════
#  CORE RESPONSE FUNCTION
# ══════════════════════════════════════════════════════════════════
def get_response(user_msg, pdf_text="", img_b64="", img_mime=""):
    client = Groq(api_key=GROQ_API_KEY)
    web_ctx, sources, used_search = "", [], False

    # Skip web search when a file is attached — the user wants the
    # file analyzed, not a web lookup of their question text.
    has_attachment = bool(pdf_text) or bool(img_b64)
    if st.session_state.web_search and needs_search(user_msg) and not has_attachment:
        with st.spinner("🌐 Searching the web…"):
            web_ctx, sources = do_web_search(user_msg)
        used_search = True

    base_prompt = st.session_state.custom_sys.strip() or PERSONAS[st.session_state.persona]["prompt"]
    system = base_prompt
    if pdf_text:
        system += (
            "\n\nIMPORTANT: The user has uploaded a PDF document. "
            "You MUST answer using ONLY the information in this document below. "
            "Do not say you cannot access the file — the full text is provided here:\n\n"
            f"--- BEGIN PDF CONTENT ---\n{pdf_text}\n--- END PDF CONTENT ---"
        )
    if web_ctx:
        system += f"\n\nLive web context:\n{web_ctx}"

    # Build history — exclude the very last message (current user msg)
    # because we append it below with image data if needed
    past_msgs = msgs()[:-1][-19:]  # up to 19 previous messages
    history = [{"role":"system","content":system}]
    for m in past_msgs:
        history.append({"role": m["role"], "content": m["content"]})

    # Force vision model when image is present
    model = st.session_state.model
    if img_b64:
        if "scout" not in model and "maverick" not in model:
            model = "meta-llama/llama-4-scout-17b-16e-instruct"
        # Append current user message WITH image as multipart content
        history.append({"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:{img_mime};base64,{img_b64}"}},
            {"type": "text",      "text": user_msg or "Please describe and analyze this image in detail."},
        ]})
    else:
        history.append({"role": "user", "content": user_msg})

    stream = client.chat.completions.create(
        model=model, messages=history,
        temperature=st.session_state.temperature,
        max_tokens=1800, stream=True,
    )
    return stream, used_search, sources, client, model

# ══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
        <div class="sb-logo-icon">✦</div>
        <div>
            <div class="sb-logo-text">SmartChat</div>
            <div class="sb-logo-sub">AI · Groq · Tavily</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    total_msgs = sum(len(v) for v in st.session_state.sessions.values())
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card"><span class="sv">{total_msgs}</span><span class="sl">messages</span></div>
        <div class="stat-card"><span class="sv">{st.session_state.total_tokens:,}</span><span class="sl">tokens</span></div>
        <div class="stat-card"><span class="sv">{len(st.session_state.sessions)}</span><span class="sl">chats</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Model
    st.markdown('<div class="sb-sec">Model</div>', unsafe_allow_html=True)
    st.session_state.model = st.selectbox(
        "", list(MODELS.keys()), format_func=lambda x: MODELS[x],
        index=list(MODELS.keys()).index(st.session_state.model) if st.session_state.model in MODELS else 0,
        label_visibility="collapsed"
    )

    # Settings
    st.markdown('<div class="sb-sec">Settings</div>', unsafe_allow_html=True)
    st.session_state.web_search     = st.toggle("🌐 Web Search",          value=st.session_state.web_search)
    st.session_state.show_followups = st.toggle("💡 Follow-up questions", value=st.session_state.show_followups)
    st.session_state.temperature    = st.slider("🌡 Temperature", 0.0, 1.0, st.session_state.temperature, 0.05)

    # Persona
    st.markdown('<div class="sb-sec">Persona</div>', unsafe_allow_html=True)
    p_items = list(PERSONAS.items())
    for row_start in range(0, len(p_items), 2):
        c1, c2 = st.columns(2)
        for ci, col in enumerate([c1, c2]):
            idx = row_start + ci
            if idx < len(p_items):
                key, p = p_items[idx]
                with col:
                    active = st.session_state.persona == key
                    if st.button(f"{p['icon']} {p['name']}", key=f"p_{key}",
                                 use_container_width=True,
                                 type="primary" if active else "secondary"):
                        st.session_state.persona = key
                        st.rerun()

    with st.expander("✏️ Custom system prompt"):
        st.session_state.custom_sys = st.text_area(
            "", value=st.session_state.custom_sys, height=90,
            placeholder="You are a specialized assistant for…",
            label_visibility="collapsed"
        )

    # Sessions
    st.markdown('<div class="sb-sec">Chats</div>', unsafe_allow_html=True)
    for sname in list(st.session_state.sessions.keys()):
        is_active = sname == st.session_state.active
        ca, cb = st.columns([5, 1])
        with ca:
            if st.button(
                ("▶ " if is_active else "  ") + sname,
                key=f"s_{sname}", use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.active = sname
                st.session_state.followups = []
                st.rerun()
        with cb:
            if len(st.session_state.sessions) > 1:
                if st.button("✕", key=f"d_{sname}"):
                    del st.session_state.sessions[sname]
                    st.session_state.active = list(st.session_state.sessions.keys())[0]
                    st.rerun()

    if st.button("＋  New Chat", use_container_width=True):
        st.session_state.sess_count += 1
        n = f"Chat {st.session_state.sess_count}"
        st.session_state.sessions[n] = []
        st.session_state.active = n
        st.session_state.followups = []
        st.rerun()

    # Export
    st.markdown('<div class="sb-sec">Export</div>', unsafe_allow_html=True)
    if msgs():
        st.download_button("📥 Download Chat (.md)", data=export_md(),
            file_name=f"smartchat_{st.session_state.active.replace(' ','_')}.md",
            mime="text/markdown", use_container_width=True)

    if st.button("🗑 Clear Chat", use_container_width=True):
        set_msgs([]); st.session_state.followups = []; st.rerun()

# ══════════════════════════════════════════════════════════════════
#  MAIN AREA
# ══════════════════════════════════════════════════════════════════
p = PERSONAS[st.session_state.persona]
st.markdown(f"""
<div class="main-header">
    <div class="main-title">SmartChat ✦</div>
    <div class="main-sub">
        <span class="status-dot"></span>
        {p['icon']} {p['name']} &nbsp;·&nbsp; {MODELS.get(st.session_state.model, st.session_state.model).split('  ')[0]}
        &nbsp;·&nbsp; Groq inference
    </div>
</div>
""", unsafe_allow_html=True)


# ── Startup check: warn immediately if key is missing ─────────
if not GROQ_API_KEY or not GROQ_API_KEY.strip():
    st.error(
        "⚠️ **GROQ_API_KEY is not set.**\n\n"
        "**On Render:** Go to your service → Environment tab → add a variable named "
        "exactly `GROQ_API_KEY` with your key (starts with `gsk_`), no quotes, no spaces. Then redeploy.\n\n"
        "**Locally:** run `export GROQ_API_KEY=gsk_yourkey` (Mac/Linux) or "
        "`set GROQ_API_KEY=gsk_yourkey` (Windows) before `streamlit run app.py`."
    )
    st.stop()

messages = msgs()

# ── Welcome screen ─────────────────────────────────────────────
if not messages:
    st.markdown('<div class="welcome-wrap"><div class="welcome-title">Try a prompt to get started</div><div class="wcard-grid">', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, (icon, title, sub) in enumerate(STARTERS):
        with cols[i % 3]:
            if st.button(f"{icon} {title}", key=f"w{i}", use_container_width=True,
                         help=sub):
                st.session_state["_inject"] = title
                st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

# ── Render messages ────────────────────────────────────────────
for idx, msg in enumerate(messages):
    ts = msg.get("time", "")
    content_text = str(msg.get("content", ""))

    if msg["role"] == "user":
        with st.chat_message("user"):
            # Show attachment badge if present
            if msg.get("has_pdf") or msg.get("has_img"):
                fname = msg.get("filename", "File")
                icon  = "📄" if msg.get("has_pdf") else "🖼"
                st.markdown(
                    f'<div style="background:rgba(124,58,237,0.15);border:1px solid ' +
                    'rgba(124,58,237,0.3);border-radius:8px;padding:5px 10px;' +
                    f'font-size:0.8rem;color:#c4b5fd;margin-bottom:6px;">{icon} {esc(fname)}</div>',
                    unsafe_allow_html=True
                )
            # st.markdown with no unsafe_allow_html — safest rendering
            st.markdown(content_text)
            if ts:
                st.caption(ts)

    else:
        with st.chat_message("assistant"):
            # Build badge row using safe inline styles only
            badge_parts = []
            if msg.get("searched"):
                badge_parts.append('<span style="background:rgba(20,83,45,0.5);color:#86efac;border:1px solid rgba(134,239,172,0.2);font-size:0.68rem;font-weight:600;padding:2px 8px;border-radius:20px;">🌐 Web</span>')
            if msg.get("has_pdf"):
                badge_parts.append('<span style="background:rgba(124,45,18,0.5);color:#fb923c;border:1px solid rgba(251,146,60,0.2);font-size:0.68rem;font-weight:600;padding:2px 8px;border-radius:20px;">📄 PDF</span>')
            if msg.get("has_img"):
                badge_parts.append('<span style="background:rgba(6,78,59,0.5);color:#6ee7b7;border:1px solid rgba(110,231,183,0.2);font-size:0.68rem;font-weight:600;padding:2px 8px;border-radius:20px;">🖼 Image</span>')
            if msg.get("persona", "default") != "default":
                pp = PERSONAS.get(msg.get("persona","default"), {})
                pname = esc(str(pp.get("name","")))
                picon = str(pp.get("icon",""))
                badge_parts.append(f'<span style="background:rgba(69,26,3,0.5);color:#fcd34d;border:1px solid rgba(252,211,77,0.2);font-size:0.68rem;font-weight:600;padding:2px 8px;border-radius:20px;">{picon} {pname}</span>')
            m_label = MODELS.get(msg.get("model",""), msg.get("model","")).split("  ")[0]
            badge_parts.append(f'<span style="background:rgba(30,27,75,0.5);color:#a5b4fc;border:1px solid rgba(165,180,252,0.2);font-size:0.68rem;font-weight:600;padding:2px 8px;border-radius:20px;">⚡ {esc(str(m_label))}</span>')

            if badge_parts:
                st.markdown(
                    '<div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:6px;">' +
                    " ".join(badge_parts) + '</div>',
                    unsafe_allow_html=True
                )

            # Bot reply — plain markdown, no unsafe_allow_html
            st.markdown(content_text)

            elapsed     = msg.get("elapsed", "")
            elapsed_str = f"{elapsed}s · " if elapsed else ""
            st.caption(f"{ts}  ·  {elapsed_str}~{msg.get('tokens', 0)} tokens")

            # Reaction buttons
            fk  = f"fb_{idx}"
            cfb = st.session_state.feedback.get(fk)
            rc1, rc2, rc3 = st.columns([1, 1, 10])
            with rc1:
                if st.button("👍" + (" ✓" if cfb == "up" else ""), key=f"u{idx}"):
                    st.session_state.feedback[fk] = "up"; st.rerun()
            with rc2:
                if st.button("👎" + (" ✓" if cfb == "down" else ""), key=f"d{idx}"):
                    st.session_state.feedback[fk] = "down"; st.rerun()

            # Sources
            if msg.get("sources"):
                with st.expander("🔗 View sources"):
                    for s in msg.get("sources", []):
                        title = str(s.get("title",""))
                        url   = str(s.get("url",""))
                        if url:
                            st.markdown(f"- [{title}]({url})")

# ── Follow-up chips ──────────────────────────────────────────────
try:
    raw_fu = st.session_state.get("followups", []) or []
    clean_followups = []
    for q in raw_fu:
        qs = str(q).strip() if q else ""
        if qs and len(qs) > 3:
            clean_followups.append(qs)
    clean_followups = clean_followups[:3]
except Exception:
    clean_followups = []

if clean_followups and messages:
    st.caption("💡 You might ask:")
    fu_cols = st.columns(len(clean_followups))
    for i, q in enumerate(clean_followups):
        with fu_cols[i]:
            btn_label = q[:60] + "…" if len(q) > 60 else q
            if st.button(btn_label, key=f"fu_{i}", use_container_width=True):
                st.session_state["_inject"] = q
                st.session_state["followups"] = []
                st.rerun()

st.markdown("<hr class='chat-divider'>", unsafe_allow_html=True)

# ── File uploaders + Send button
# NOTE: base64/pdf text are stored in session_state BEFORE rerun
# because file handles become invalid after st.rerun()
uploaded_pdf = None
uploaded_img = None

with st.expander("📎  Attach file  (📄 PDF  or  🖼 Image)", expanded=False):
    col_pdf, col_img = st.columns(2)
    with col_pdf:
        st.markdown("**📄 Upload PDF**")
        uploaded_pdf = st.file_uploader("", type=["pdf"], key="pdf_up", label_visibility="collapsed")
        if uploaded_pdf:
            st.success(f"✓ {uploaded_pdf.name} ready")
    with col_img:
        st.markdown("**🖼 Upload Image**")
        uploaded_img = st.file_uploader("", type=["png","jpg","jpeg","webp","gif"], key="img_up", label_visibility="collapsed")
        if uploaded_img:
            try:
                img_preview = Image.open(uploaded_img)
                uploaded_img.seek(0)
                st.image(img_preview, width=220)
                st.success(f"✓ {uploaded_img.name} ready — add a question and click Send")
            except:
                pass

    if uploaded_pdf and uploaded_img:
        st.warning("⚠️ Please send only ONE file at a time (PDF or Image, not both). Remove one to continue.")

    elif uploaded_pdf or uploaded_img:
        attached_file = uploaded_pdf or uploaded_img
        att_q = st.text_input(
            "", key="att_question",
            placeholder="Ask something about this file… (leave blank to auto-describe)",
            label_visibility="collapsed"
        )
        send_col, _ = st.columns([1, 4])
        with send_col:
            if st.button("➤ Send to AI", key="att_send", use_container_width=True, type="primary"):
                # ★ Convert files to bytes/base64 RIGHT NOW before rerun kills the file handles
                if att_q.strip():
                    prompt = att_q.strip()
                elif uploaded_img:
                    prompt = "Please describe and analyze this image in detail."
                else:
                    prompt = "Please summarize and explain the key points of this PDF."

                if uploaded_pdf:
                    pdf_bytes_text = extract_pdf_text(uploaded_pdf)
                    if pdf_bytes_text.startswith("[PDF extraction error"):
                        st.error(f"❌ PDF extraction failed: {pdf_bytes_text}")
                        st.stop()
                    if not pdf_bytes_text.strip():
                        st.error("❌ No text could be extracted from this PDF (it may be a scanned/image-only PDF).")
                        st.stop()
                    st.session_state["_att_pdf_text"] = pdf_bytes_text
                    st.session_state["_att_pdf_name"] = uploaded_pdf.name

                elif uploaded_img:
                    b64, mime = image_to_base64(uploaded_img)
                    if not b64:
                        st.error("❌ Could not read the image file. Try a different file.")
                        st.stop()
                    st.session_state["_att_img_b64"]  = b64
                    st.session_state["_att_img_mime"] = mime
                    st.session_state["_att_img_name"] = uploaded_img.name

                st.session_state["_inject"] = prompt
                st.rerun()

# ── Chat input
user_input = st.chat_input("Ask me anything…")

if "_inject" in st.session_state:
    user_input = st.session_state.pop("_inject")

# Pull pre-encoded attachment data stored before rerun
pdf_text  = st.session_state.pop("_att_pdf_text", "")
pdf_fname = st.session_state.pop("_att_pdf_name", "")
img_b64_s = st.session_state.pop("_att_img_b64",  "")
img_mime_s= st.session_state.pop("_att_img_mime", "")
img_fname = st.session_state.pop("_att_img_name", "")

if user_input:
    now = datetime.now().strftime("%H:%M")
    has_pdf = bool(pdf_text)
    has_img = bool(img_b64_s)
    filename = pdf_fname or img_fname or ""

    # Also handle plain file upload without the Send button (normal chat)
    if uploaded_pdf and not pdf_text:
        with st.spinner("📄 Reading PDF…"):
            pdf_text = extract_pdf_text(uploaded_pdf)
        has_pdf  = True
        filename = uploaded_pdf.name

    if uploaded_img and not img_b64_s:
        img_b64_s, img_mime_s = image_to_base64(uploaded_img)
        has_img  = True
        filename = uploaded_img.name


    # Save user message
    user_entry = {
        "role": "user", "content": user_input, "time": now,
        "has_pdf": has_pdf, "has_img": has_img, "filename": filename,
    }
    m = msgs(); m.append(user_entry); set_msgs(m)

    # Auto-title on first message
    if len(msgs()) == 1:
        try:
            ct = Groq(api_key=GROQ_API_KEY)
            title = auto_title(user_input, ct)
            old = st.session_state.active
            if title and title != old:
                st.session_state.sessions[title] = st.session_state.sessions.pop(old)
                st.session_state.active = title
        except:
            pass

    try:
        stream, used_search, sources, groq_client, used_model = get_response(
            user_input, pdf_text, img_b64_s, img_mime_s
        )

        full_reply = ""
        t0 = time.time()

        with st.chat_message("assistant"):
            placeholder = st.empty()
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_reply += delta
                placeholder.markdown(full_reply + "▌")
            placeholder.markdown(full_reply)

        elapsed = round(time.time() - t0, 1)
        estimated_tokens = len(full_reply) // 4
        st.session_state.total_tokens += estimated_tokens

        m = msgs()
        m.append({
            "role": "assistant", "content": full_reply,
            "searched": used_search, "sources": sources,
            "time": now, "model": used_model,
            "persona": st.session_state.persona,
            "elapsed": elapsed, "tokens": estimated_tokens,
            "has_pdf": has_pdf, "has_img": has_img,
        })
        set_msgs(m)

        if st.session_state.show_followups and len(msgs()) >= 2:
            st.session_state.followups = get_followups(msgs(), groq_client)

        st.rerun()

    except Exception as e:
        err = str(e)
        if "auth" in err.lower() or "api_key" in err.lower() or "401" in err:
            st.error(
                "❌ Invalid or missing Groq API key.\n\n"
                "**If deployed on Render:** go to your service → Environment tab → "
                "check GROQ_API_KEY has no extra spaces or quotes around the value, then redeploy.\n\n"
                "**If running locally:** set the GROQ_API_KEY environment variable before running streamlit.\n\n"
                f"Raw error: {err}"
            )
        elif "rate" in err.lower():
            st.error("⚠️ Rate limit hit — wait a moment and retry")
        elif "model" in err.lower():
            st.error(f"❌ Model error: {err}")
        else:
            st.error(f"❌ {err}")
