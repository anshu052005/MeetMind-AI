"""
MeetMind AI — Meeting Intelligence Dashboard
----------------------------------------------
Transcribe, summarise, and chat with meeting recordings (YouTube or local files).
"""

import html
import logging
import time
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

# ─── Environment & Logging ───────────────────────────────────────────────────────
load_dotenv(Path(__file__).parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("meetmind")

# ─── Constants ────────────────────────────────────────────────────────────────
PIPELINE_STEPS = [
    ("audio", "🔊", "Audio Processing"),
    ("transcript", "📝", "Transcription"),
    ("title", "🏷️", "Title Generation"),
    ("summary", "📋", "Summarisation"),
    ("extract", "🔍", "Extraction"),
    ("rag", "🧠", "RAG Engine"),
]
LANGUAGES = ["english", "hinglish"]

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MeetMind AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
    --bg: #0d1117;
    --surface: #151b23;
    --surface-2: #1c242e;
    --border: #2b3440;
    --accent: #3b6dd8;
    --accent-glow: #5b8def;
    --accent-2: #0ea5a0;
    --text: #e6e9ef;
    --text-muted: #8891a0;
    --success: #22c55e;
    --warning: #d69e2e;
    --danger: #e5484d;
}

html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background: var(--bg) !important; }

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(59, 109, 216, 0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59, 109, 216, 0.025) 1px, transparent 1px);
    background-size: 44px 44px;
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

h1, h2, h3, h4, h5, h6 { font-family: 'Inter', sans-serif !important; color: var(--text) !important; }

.hero-title {
    font-family: 'Inter', sans-serif;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 800;
    line-height: 1.1;
    margin: 0;
    background: linear-gradient(120deg, #f2f4f8 0%, var(--accent-glow) 65%, var(--accent-2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.card:hover { border-color: var(--accent); }
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--accent), var(--accent-2));
}

.card-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-content {
    font-size: 0.875rem;
    line-height: 1.7;
    color: var(--text);
    white-space: pre-wrap;
    word-break: break-word;
}

.badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.badge-purple { background: rgba(59,109,216,0.2); color: var(--accent-glow); border: 1px solid rgba(59,109,216,0.3); }
.badge-cyan   { background: rgba(6,182,212,0.15); color: var(--accent-2);    border: 1px solid rgba(6,182,212,0.3); }
.badge-green  { background: rgba(16,185,129,0.15); color: var(--success);    border: 1px solid rgba(16,185,129,0.3); }
.badge-red    { background: rgba(239,68,68,0.15);  color: var(--danger);     border: 1px solid rgba(239,68,68,0.3); }

.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(59,109,216,0.2) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent), #274a9e) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(59,109,216,0.28) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
}

.status-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: var(--surface-2);
    border-radius: 8px;
    margin: 0.4rem 0;
    border: 1px solid var(--border);
    font-size: 0.8rem;
}
.status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-active   { background: var(--accent-glow); box-shadow: 0 0 5px var(--accent-glow); animation: pulse 1.5s infinite; }
.dot-done     { background: var(--success); }
.dot-pending  { background: var(--border); }
.dot-error    { background: var(--danger); }

@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

.chat-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    max-height: 420px;
    overflow-y: auto;
    margin-bottom: 1rem;
}
.chat-msg { margin-bottom: 1rem; display: flex; flex-direction: column; gap: 0.2rem; }
.chat-label { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; }
.chat-bubble {
    display: inline-block;
    padding: 0.6rem 1rem;
    border-radius: 10px;
    font-size: 0.85rem;
    line-height: 1.6;
    max-width: 90%;
    white-space: pre-wrap;
    word-break: break-word;
}
.user-label  { color: var(--accent-glow); }
.bot-label   { color: var(--accent-2); }
.user-bubble { background: rgba(59,109,216,0.15); border: 1px solid rgba(59,109,216,0.25); align-self: flex-end; }
.bot-bubble  { background: rgba(6,182,212,0.1);  border: 1px solid rgba(6,182,212,0.2);   align-self: flex-start; }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }

.transcript-box {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
    font-size: 0.82rem;
    line-height: 1.8;
    max-height: 300px;
    overflow-y: auto;
    color: var(--text-muted);
    white-space: pre-wrap;
    word-break: break-word;
}

.stProgress > div > div > div { background: var(--accent) !important; }
.stSpinner > div { border-top-color: var(--accent) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text) !important; }
label { color: var(--text-muted) !important; font-size: 0.8rem !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
DEFAULT_STATE = {
    "result": None,
    "chat_history": [],
    "pipeline_done": False,
    "pipeline_steps": {},
    "pipeline_error": None,
    "chat_input_key": 0,   # bump this to reset the chat text_input widget
}
for key, default in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ─── Helpers ────────────────────────────────────────────────────────────────────
def safe_html(text) -> str:
    """Escape any dynamic/model-generated text before injecting into markdown HTML."""
    if text is None:
        return ""
    return html.escape(str(text))


def is_probable_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def validate_source(value: str) -> str | None:
    """Return an error message if the source is invalid, else None."""
    value = value.strip()
    if not value:
        return "Please enter a YouTube URL or file path."
    if is_probable_url(value):
        if "youtube.com" not in value and "youtu.be" not in value:
            return "Only YouTube URLs are supported for links. For local media, provide a file path instead."
        return None
    if not Path(value).exists():
        return f"File not found: {value}"
    return None


def step_status_class(steps: dict, key: str) -> str:
    return {
        "active": "dot-active",
        "done": "dot-done",
        "error": "dot-error",
    }.get(steps.get(key, "pending"), "dot-pending")


def render_step_bar(label: str, key: str, icon: str):
    css_class = step_status_class(st.session_state.pipeline_steps, key)
    st.markdown(
        f"""<div class="status-bar">
            <div class="status-dot {css_class}"></div>
            <span>{icon} {label}</span>
        </div>""",
        unsafe_allow_html=True,
    )


def reset_pipeline_state():
    st.session_state.pipeline_done = False
    st.session_state.result = None
    st.session_state.chat_history = []
    st.session_state.pipeline_steps = {}
    st.session_state.pipeline_error = None


def run_pipeline(source: str, language: str):
    """Run the full processing pipeline with per-step status + error handling."""
    steps_ui = st.status("Running analysis pipeline…", expanded=True)

    def mark(key: str, state: str, note: str = ""):
        st.session_state.pipeline_steps[key] = state
        icon_map = {"active": "⏳", "done": "✅", "error": "❌"}
        label_map = dict((k, lbl) for k, _, lbl in PIPELINE_STEPS)
        steps_ui.write(f"{icon_map.get(state, '•')} {label_map[key]} {note}")

    try:
        mark("audio", "active")
        chunks = process_input(source)
        mark("audio", "done")

        mark("transcript", "active")
        transcript = transcribe_all(chunks, language)
        if not transcript or not transcript.strip():
            raise ValueError("Transcription returned empty text.")
        mark("transcript", "done")

        mark("title", "active")
        title = generate_title(transcript)
        mark("title", "done")

        mark("summary", "active")
        summary = summarize(transcript)
        mark("summary", "done")

        mark("extract", "active")
        action_items = extract_action_items(transcript)
        decisions = extract_key_decisions(transcript)
        questions = extract_questions(transcript)
        mark("extract", "done")

        mark("rag", "active")
        rag_chain = build_rag_chain(transcript)
        mark("rag", "done")

        st.session_state.result = {
            "title": title,
            "transcript": transcript,
            "summary": summary,
            "action_items": action_items,
            "key_decisions": decisions,
            "open_questions": questions,
            "rag_chain": rag_chain,
        }
        st.session_state.pipeline_done = True
        steps_ui.update(label="Analysis complete", state="complete", expanded=False)

    except Exception as exc:
        logger.exception("Pipeline failed at source=%s", source)
        for k, _, _ in PIPELINE_STEPS:
            if st.session_state.pipeline_steps.get(k) == "active":
                st.session_state.pipeline_steps[k] = "error"
        st.session_state.pipeline_error = str(exc)
        steps_ui.update(label="Analysis failed", state="error", expanded=True)


# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hero-title" style="font-size:1.6rem">🎬 AI<br>Video</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Meeting Intelligence</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<span class="badge badge-purple">Input</span>', unsafe_allow_html=True)
    source = st.text_input(
        "YouTube URL or File Path",
        placeholder="https://youtube.com/watch?v=... or /path/to/file.mp4",
    ).strip()

    language = st.selectbox("Language", LANGUAGES, index=0)

    run_btn = st.button("⚡  Analyse", use_container_width=True)

    if st.session_state.pipeline_done or st.session_state.result:
        if st.button("🔄  New Analysis", use_container_width=True, type="secondary"):
            reset_pipeline_state()
            st.rerun()

    if st.session_state.pipeline_steps:
        st.markdown("---")
        badge_class = "badge-red" if st.session_state.pipeline_error else "badge-green"
        badge_text = "Pipeline Error" if st.session_state.pipeline_error else "Pipeline Status"
        st.markdown(f'<span class="badge {badge_class}">{badge_text}</span>', unsafe_allow_html=True)
        for step_key, icon, label in PIPELINE_STEPS:
            render_step_bar(label, step_key, icon)

# ─── Main Area ──────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">MeetMind AI</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Transcribe · Summarise · Chat with your meetings</div>', unsafe_allow_html=True)
st.markdown("---")

# ── Run Pipeline ────────────────────────────────────────────────────────────────
if run_btn:
    error_msg = validate_source(source)
    if error_msg:
        st.error(f"⚠️ {error_msg}")
    else:
        reset_pipeline_state()
        run_pipeline(source, language)
        if st.session_state.pipeline_done:
            time.sleep(0.3)
            st.rerun()

if st.session_state.pipeline_error and not st.session_state.pipeline_done:
    st.error(f"❌ Analysis failed: {safe_html(st.session_state.pipeline_error)}")

# ── Results ──────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    st.markdown(f"""
    <div class="card">
        <div class="card-title">📌 Session Title</div>
        <div style="font-family:'Inter',sans-serif;font-size:1.4rem;font-weight:700;color:var(--text)">
            {safe_html(r['title'])}
        </div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📋 Summary</div>
            <div class="card-content">{safe_html(r['summary'])}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        with st.expander("📝 Full Transcript", expanded=False):
            st.markdown(f'<div class="transcript-box">{safe_html(r["transcript"])}</div>', unsafe_allow_html=True)
            st.download_button(
                "⬇️ Download Transcript",
                data=r["transcript"],
                file_name="transcript.txt",
                use_container_width=True,
            )

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">✅ Action Items</div>
            <div class="card-content">{safe_html(r['action_items'])}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">🔑 Key Decisions</div>
            <div class="card-content">{safe_html(r['key_decisions'])}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">❓ Open Questions</div>
            <div class="card-content">{safe_html(r['open_questions'])}</div>
        </div>""", unsafe_allow_html=True)

    # Consolidated report download
    report_text = (
        f"Title: {r['title']}\n\n"
        f"Summary:\n{r['summary']}\n\n"
        f"Action Items:\n{r['action_items']}\n\n"
        f"Key Decisions:\n{r['key_decisions']}\n\n"
        f"Open Questions:\n{r['open_questions']}\n"
    )
    st.download_button("⬇️ Download Full Report", data=report_text, file_name="meeting_report.txt")

    st.markdown("---")

    # ── RAG Chat ──────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-family:\'Inter\',sans-serif;font-size:1.2rem;font-weight:700;margin-bottom:1rem">'
        '💬 Chat with your Meeting</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            role_class = "user" if msg["role"] == "user" else "bot"
            label = "You" if msg["role"] == "user" else "🤖 Assistant"
            align = "flex-end" if msg["role"] == "user" else "flex-start"
            chat_html += f"""
            <div class="chat-msg" style="align-items:{align}">
                <span class="chat-label {role_class}-label">{label}</span>
                <div class="chat-bubble {role_class}-bubble">{safe_html(msg['content'])}</div>
            </div>"""
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:2rem">
            <div style="font-size:2rem;margin-bottom:0.5rem">💬</div>
            <div style="color:var(--text-muted);font-size:0.85rem">Ask anything about your meeting transcript</div>
        </div>""", unsafe_allow_html=True)

    # Use a form so Enter submits and the input clears automatically afterwards.
    with st.form(key=f"chat_form_{st.session_state.chat_input_key}", clear_on_submit=True):
        chat_col1, chat_col2 = st.columns([5, 1], gap="small")
        with chat_col1:
            user_input = st.text_input(
                "Your question",
                placeholder="What were the main decisions made?",
                label_visibility="collapsed",
            )
        with chat_col2:
            send_btn = st.form_submit_button("Send →", use_container_width=True)

    if send_btn:
        question = user_input.strip()
        if not question:
            st.warning("Please type a question first.")
        else:
            try:
                with st.spinner("Thinking…"):
                    answer = ask_question(r["rag_chain"], question)
            except Exception as exc:
                logger.exception("RAG query failed")
                answer = f"⚠️ Sorry, I couldn't answer that: {exc}"
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:5rem 2rem;text-align:center">
        <div style="font-size:4rem;margin-bottom:1rem">🎬</div>
        <div style="font-family:'Inter',sans-serif;font-size:1.5rem;font-weight:700;color:var(--text);margin-bottom:0.5rem">
            Ready to Analyse
        </div>
        <div style="color:var(--text-muted);font-size:0.85rem;max-width:380px;line-height:1.7">
            Paste a YouTube URL or local file path in the sidebar, choose your language, and hit <strong>Analyse</strong> to get started.
        </div>
        <div style="margin-top:2rem;display:flex;gap:1rem;flex-wrap:wrap;justify-content:center">
            <span class="badge badge-purple">Transcription</span>
            <span class="badge badge-cyan">Summarisation</span>
            <span class="badge badge-green">RAG Chat</span>
        </div>
    </div>""", unsafe_allow_html=True)