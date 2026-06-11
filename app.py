import streamlit as st
from groq import Groq
from tavily import TavilyClient
import html, json, time, re, base64
from datetime import datetime
from PIL import Image
from io import BytesIO

# ╔══════════════════════════════════════════════════════════════════╗
# ║                     API KEYS  (edit here)                       ║
# ╚══════════════════════════════════════════════════════════════════╝
GROQ_API_KEY   = "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"
TAVILY_API_KEY = "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"

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
    "llama-3.3-70b-versatile":                        "LLaMA 3.3 70B  ★ Best",
    "llama-3.1-8b-instant":                           "LLaMA 3.1 8B  ⚡ Fast",
    "meta-llama/llama-4-scout-17b-16e-instruct":      "LLaMA 4 Scout  👁 Vision",
    "meta-llama/llama-4-maverick-17b-128e-instruct":  "LLaMA 4 Maverick",
    "qwen/qwen-3-32b":                                "Qwen 3 32B",
    "mixtral-8x7b-32768":                             "Mixtral 8x7B",
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
        data = uploaded_file.read()
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

def image_to_base64(uploaded_file) -> tuple[str, str]:
    """Convert uploaded image to base64 for vision models."""
    data   = uploaded_file.read()
    b64    = base64.b64encode(data).decode("utf-8")
    suffix = uploaded_file.name.split(".")[-1].lower()
    mime   = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
              "png": "image/png",  "webp": "image/webp",
              "gif": "image/gif"}.get(suffix, "image/jpeg")
    return b64, mime

def do_web_search(query: str) -> tuple[str, list]:
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
        ctx = "\n".join([f"{m['role']}: {m['content'][:150]}" for m in history[-4:]])
        r   = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content":f"Conversation:\n{ctx}\n\nSuggest 3 short follow-up questions. JSON array only."}],
            max_tokens=120, temperature=0.8,
        )
        raw = re.sub(r"```json|```","", r.choices[0].message.content).strip()
        return json.loads(raw)
    except:
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

    if st.session_state.web_search and needs_search(user_msg):
        with st.spinner("🌐 Searching the web…"):
            web_ctx, sources = do_web_search(user_msg)
        used_search = True

    base_prompt = st.session_state.custom_sys.strip() or PERSONAS[st.session_state.persona]["prompt"]
    system = base_prompt
    if pdf_text:
        system += f"\n\nThe user has uploaded a PDF. Its content:\n{pdf_text}"
    if web_ctx:
        system += f"\n\nLive web context:\n{web_ctx}"

    history = [{"role":"system","content":system}]
    for m in msgs()[-20:]:
        history.append({"role": m["role"], "content": m["content"]})

    # Vision model for images
    model = st.session_state.model
    if img_b64:
        if "scout" not in model and "maverick" not in model:
            model = "meta-llama/llama-4-scout-17b-16e-instruct"
        history.append({"role":"user","content":[
            {"type":"image_url","image_url":{"url":f"data:{img_mime};base64,{img_b64}"}},
            {"type":"text","text": user_msg or "Describe this image in detail."},
        ]})
    else:
        history.append({"role":"user","content":user_msg})

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
        index=list(MODELS.keys()).index(st.session_state.model),
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
st.markdown('<div class="chat-area">', unsafe_allow_html=True)
for idx, msg in enumerate(messages):
    ts = msg.get("time", "")
    if msg["role"] == "user":
        attach_html = ""
        if msg.get("has_pdf"):
            attach_html = f'<div class="attach-preview">📄 {esc(msg.get("filename","PDF"))}</div>'
        if msg.get("has_img"):
            attach_html = f'<div class="attach-preview">🖼 {esc(msg.get("filename","Image"))}</div>'
        st.markdown(f"""
        <div class="bubble-wrap-user">
            <div>
                {attach_html}
                <div class="bubble-user">{esc(msg["content"])}</div>
                <div class="bubble-meta-user">{ts}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        badges_html = '<div class="badges">'
        if msg.get("searched"):
            badges_html += '<span class="badge badge-web">🌐 Web</span>'
        if msg.get("has_pdf"):
            badges_html += '<span class="badge badge-pdf">📄 PDF</span>'
        if msg.get("has_img"):
            badges_html += '<span class="badge badge-img">🖼 Image</span>'
        if msg.get("persona","default") != "default":
            pp = PERSONAS.get(msg["persona"], {})
            badges_html += f'<span class="badge badge-persona">{pp.get("icon","")} {pp.get("name","")}</span>'
        m_label = MODELS.get(msg.get("model",""), msg.get("model","")).split("  ")[0]
        badges_html += f'<span class="badge badge-model">⚡ {esc(m_label)}</span>'
        badges_html += '</div>'

        st.markdown(f"""
        <div class="bubble-wrap-bot">
            <div class="bot-avatar">✦</div>
            <div style="max-width:80%">
                {badges_html}
                <div class="bubble-bot">
        """, unsafe_allow_html=True)
        st.markdown(msg["content"])
        st.markdown(f"""
                </div>
                <div class="bubble-meta-bot">{ts} · {msg.get('elapsed','')}{('s' if msg.get('elapsed') else '')} · ~{msg.get('tokens',0)} tokens</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Reactions
        fk = f"fb_{idx}"
        cfb = st.session_state.feedback.get(fk)
        rc1, rc2, rc3 = st.columns([1, 1, 10])
        with rc1:
            if st.button("👍" + (" ✓" if cfb=="up" else ""), key=f"u{idx}"):
                st.session_state.feedback[fk] = "up"; st.rerun()
        with rc2:
            if st.button("👎" + (" ✓" if cfb=="down" else ""), key=f"d{idx}"):
                st.session_state.feedback[fk] = "down"; st.rerun()

        # Sources expander
        if msg.get("sources"):
            with st.expander("🔗 View sources"):
                for s in msg["sources"]:
                    st.markdown(f"- [{s['title']}]({s['url']})")

st.markdown('</div>', unsafe_allow_html=True)  # chat-area

# ── Follow-up chips ────────────────────────────────────────────
if st.session_state.followups and messages:
    st.markdown('<div class="fu-wrap"><div class="fu-label">💡 You might ask:</div></div>', unsafe_allow_html=True)
    fu_cols = st.columns(len(st.session_state.followups))
    for i, q in enumerate(st.session_state.followups):
        with fu_cols[i]:
            if st.button(q, key=f"fu{i}", use_container_width=True):
                st.session_state["_inject"] = q
                st.session_state.followups = []
                st.rerun()

st.markdown("<hr class='chat-divider'>", unsafe_allow_html=True)

# ── File upload strip ──────────────────────────────────────────
with st.expander("📎 Attach file  ( PDF or Image )", expanded=False):
    col_pdf, col_img = st.columns(2)
    with col_pdf:
        st.markdown("**📄 Upload PDF**")
        uploaded_pdf = st.file_uploader("", type=["pdf"], key="pdf_up", label_visibility="collapsed")
    with col_img:
        st.markdown("**🖼 Upload Image**")
        uploaded_img = st.file_uploader("", type=["png","jpg","jpeg","webp","gif"], key="img_up", label_visibility="collapsed")
        if uploaded_img:
            try:
                img = Image.open(uploaded_img)
                uploaded_img.seek(0)
                st.image(img, width=180)
            except:
                pass

# ── Chat input ─────────────────────────────────────────────────
user_input = st.chat_input("Ask me anything…  (or attach a PDF / image above)")

if "_inject" in st.session_state:
    user_input = st.session_state.pop("_inject")

if user_input:
    now = datetime.now().strftime("%H:%M")
    pdf_text = img_b64 = img_mime = filename = ""
    has_pdf = has_img = False

    if uploaded_pdf:
        with st.spinner("📄 Reading PDF…"):
            pdf_text = extract_pdf_text(uploaded_pdf)
        has_pdf  = True
        filename = uploaded_pdf.name

    if uploaded_img:
        img_b64, img_mime = image_to_base64(uploaded_img)
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
            user_input, pdf_text, img_b64, img_mime
        )

        placeholder = st.empty()
        full_reply  = ""
        t0 = time.time()

        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_reply += delta
            placeholder.markdown(full_reply + "▌")

        elapsed = round(time.time() - t0, 1)
        estimated_tokens = len(full_reply) // 4
        st.session_state.total_tokens += estimated_tokens

        placeholder.markdown(full_reply)

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
        if "auth" in err.lower() or "api_key" in err.lower():
            st.error("❌ Invalid API key — check GROQ_API_KEY at the top of app.py")
        elif "rate" in err.lower():
            st.error("⚠️ Rate limit hit — wait a moment and retry")
        elif "model" in err.lower():
            st.error(f"❌ Model error: {err}")
        else:
            st.error(f"❌ {err}")
