import html
import time
import os   
import streamlit as st
 
from src.rag import ask_question
from src.ingest import ingest_pdf
 
# ============================================================
# PAGE CONFIG
# ============================================================
 
st.set_page_config(
    page_title="Research AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
USER_AVATAR = "🖋️"
ASSISTANT_AVATAR = "📚"
 
 
# ============================================================
# HELPERS
# ============================================================
 
def md_html(markup: str) -> None:
    """Render an HTML snippet safely.
 
    Streamlit runs st.markdown through a Markdown parser first. Indented
    lines that follow a blank line are treated as code blocks, which prints
    raw HTML on screen. Flattening the snippet to a single line avoids that.
    """
    flat = " ".join(
        line.strip() for line in markup.strip().splitlines() if line.strip()
    )
    st.markdown(flat, unsafe_allow_html=True)
 
 
# ============================================================
# CSS
# ============================================================
 
STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&display=swap');
 
:root {
    --bg: #080b14;
    --surface: #111726;
    --surface2: #161d31;
    --border: #252e43;
    --text: #f4f6fb;
    --text-soft: #c9cfde;
    --muted: #8993a8;
    --accent: #7c8cff;
    --accent2: #5364e8;
    --warning: #ffd166;
    --serif: 'Newsreader', Georgia, serif;
    --sans: 'DM Sans', system-ui, sans-serif;
}
 
/* ---------- App shell ---------- */
 
.stApp {
    background:
        radial-gradient(900px 500px at 70% -10%, rgba(84,100,232,.16), transparent 65%),
        var(--bg);
    color: var(--text);
    font-family: var(--sans);
}
 
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
 
.block-container {
    max-width: 860px;
    margin: 0 auto;
    padding-top: 2.2rem;
    padding-bottom: 8rem;
}
 
/* Default text colours for dark mode, whatever theme Streamlit starts in */
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li {
    color: var(--text-soft);
}
.stApp [data-testid="stMarkdownContainer"] h1,
.stApp [data-testid="stMarkdownContainer"] h2,
.stApp [data-testid="stMarkdownContainer"] h3,
.stApp [data-testid="stMarkdownContainer"] h4 {
    color: var(--text);
    font-family: var(--serif);
    font-weight: 500;
}
.stApp [data-testid="stMarkdownContainer"] strong { color: var(--text); }
.stApp [data-testid="stMarkdownContainer"] a { color: var(--accent); }
.stApp [data-testid="stMarkdownContainer"] code {
    background: rgba(124,140,255,.14);
    color: #c5cdff;
    border-radius: 6px;
    padding: .1em .4em;
}
 
/* ---------- Sidebar ---------- */
 
section[data-testid="stSidebar"] {
    background: #090d18;
    border-right: 1px solid var(--border);
}
 
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 26px;
}
.sidebar-logo {
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    font-size: 21px;
    box-shadow: 0 8px 25px rgba(84,100,232,.35);
}
.sidebar-title { font-size: 1rem; font-weight: 700; color: var(--text); }
.sidebar-subtitle { font-size: .75rem; color: var(--muted); margin-top: 2px; }
 
.sidebar-section {
    color: var(--muted);
    font-size: .8rem;
    font-weight: 600;
    margin: 26px 0 10px 0;
}
 
.status-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 14px;
}
.status-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 11px;
}
.status-row:last-child { margin-bottom: 0; }
.status-label { color: var(--muted); font-size: .8rem; }
.status-value { color: var(--text); font-size: .8rem; font-weight: 600; }
 
.sidebar-info { color: var(--muted); font-size: .78rem; line-height: 1.7; }
 
section[data-testid="stSidebar"] .stButton,
section[data-testid="stSidebar"] [data-testid="stButton"] {
    width: 100%;
}
[data-testid="stBottomBlockContainer"] {
    max-width: 860px;
    margin: 0 auto;
}
section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text-soft);
    border-radius: 10px;
    transition: border-color .15s, color .15s;
}
section[data-testid="stSidebar"] .stButton > button:hover:not(:disabled) {
    border-color: var(--accent);
    color: #fff;
}
section[data-testid="stSidebar"] .stButton > button:disabled { opacity: .45; }
 
/* ---------- Hero and top bar ---------- */
 
.hero { padding: 40px 0 26px 0; }
.hero h1 {
    font-family: var(--serif);
    font-weight: 500;
    font-size: 3.1rem;
    line-height: 1.05;
    letter-spacing: -.03em;
    color: var(--text);
    margin: 0;
    padding: 0;
}
.hero-sub {
    margin-top: 16px;
    max-width: 560px;
    color: var(--muted);
    font-size: 1.02rem;
    line-height: 1.65;
}
.hero-hint {
    margin-top: 24px;
    max-width: 560px;
    padding: 14px 16px;
    border: 1px dashed var(--border);
    border-radius: 12px;
    color: var(--muted);
    font-size: .9rem;
    line-height: 1.6;
}
 
.topbar {
    display: flex;
    align-items: baseline;
    gap: 14px;
    flex-wrap: wrap;
    padding-bottom: 14px;
    margin-bottom: 8px;
    border-bottom: 1px solid var(--border);
}
.topbar-title { font-family: var(--serif); font-size: 1.5rem; color: var(--text); }
.topbar-sub { color: var(--muted); font-size: .9rem; }
 
/* ---------- Chat ---------- */
 
[data-testid="stChatMessage"] {
    background: transparent;
    padding: 8px 0;
    gap: 14px;
}
[data-testid^="stChatMessageAvatar"] {
    background: var(--surface);
    border: 1px solid var(--border);
}
 
/* Assistant answers read like a page of text */
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
    font-family: var(--serif);
    font-size: 1.14rem;
    line-height: 1.75;
    color: #e8ebf3;
}
 
/* Questions sit in a soft bubble */
.who-user {
    display: inline-block;
    max-width: 100%;
    background: rgba(124,140,255,.12);
    border: 1px solid rgba(124,140,255,.2);
    border-radius: 18px 18px 18px 5px;
    padding: 9px 16px;
    color: var(--text);
    font-family: var(--sans);
    font-size: .98rem;
    font-weight: 500;
    line-height: 1.55;
}
 
.meta { margin-top: 14px; color: var(--muted); font-size: .78rem; }
 
/* ---------- Sources ---------- */
 
.sources {
    margin-top: 24px;
    padding-top: 14px;
    border-top: 1px solid var(--border);
}
.sources-head { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.sources-title { font-family: var(--serif); font-size: 1.3rem; font-weight: 600; color: var(--text); }
.sources-count {
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--muted);
    font-size: .75rem;
    font-weight: 600;
    padding: 1px 9px;
    border-radius: 999px;
}
 
.source {
    background: linear-gradient(135deg, var(--surface), var(--surface2));
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 12px;
    margin-top: 8px;
    overflow: hidden;
}
.source summary {
    list-style: none;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    cursor: pointer;
}
.source summary::-webkit-details-marker { display: none; }
.source summary:hover { background: rgba(124,140,255,.06); }
.source summary:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; }
 
.source-n {
    width: 27px;
    height: 27px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    color: #fff;
    font-size: .78rem;
    font-weight: 700;
}
.source-name {
    flex: 1;
    min-width: 0;
    color: var(--text);
    font-size: .88rem;
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.source-page {
    flex-shrink: 0;
    background: rgba(255,209,102,.1);
    color: var(--warning);
    border: 1px solid rgba(255,209,102,.22);
    font-size: .74rem;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 999px;
}
.source-toggle { flex-shrink: 0; color: var(--accent); font-size: .78rem; font-weight: 500; }
.source-toggle::after {
    content: "▾";
    display: inline-block;
    margin-left: 6px;
    transition: transform .2s;
}
.source[open] .source-toggle::after { transform: rotate(180deg); }
 
.passage {
    border-top: 1px dashed var(--border);
    padding: 14px 18px 16px 18px;
    font-family: var(--serif);
    font-size: 1.02rem;
    line-height: 1.75;
    color: var(--text-soft);
}
 
/* ---------- Input ---------- */
 
[data-testid="stBottom"] > div {
    background: linear-gradient(to top, var(--bg) 65%, transparent);
}
[data-testid="stChatInput"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
    box-shadow: 0 10px 40px rgba(0,0,0,.35);
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent);
    box-shadow: 0 10px 40px rgba(84,100,232,.22);
}
/* Light input bar with dark text, so what you type is always readable */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] div[data-baseweb="textarea"],
[data-testid="stChatInput"] div[data-baseweb="base-input"] {
    background: #F4F6FB !important;
    border-radius: 18px;
}
[data-testid="stChatInput"]:focus-within,
[data-testid="stChatInput"]:focus-within > div,
[data-testid="stChatInput"] div[data-baseweb="textarea"],
[data-testid="stChatInput"] div[data-baseweb="base-input"] {
    border-color: var(--accent) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #101B34 !important;
    -webkit-text-fill-color: #101B34 !important;
    caret-color: #101B34;
    font-family: var(--sans);
    font-weight: 500;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #6B7489 !important;
    -webkit-text-fill-color: #6B7489 !important;
    opacity: 1;
}
[data-testid="stChatInput"] button {
    background: var(--accent2) !important;
    color: #fff !important;
    border-radius: 10px;
}
[data-testid="stChatInput"] button svg { fill: #fff; color: #fff; }
 
/* ---------- Misc ---------- */
 
[data-testid="stSpinner"], [data-testid="stSpinner"] * { color: var(--muted); }
 
@media (prefers-reduced-motion: reduce) {
    * { transition: none !important; }
}
 
@media (max-width: 800px) {
    .hero h1 { font-size: 2.3rem; }
    .source-toggle { display: none; }
}
</style>
"""
 
md_html(STYLE)
 
 
# ============================================================
# RENDERERS
# ============================================================
 
def render_user(text: str) -> None:
    safe = html.escape(text).replace("\n", "<br>")
    md_html(f'<div class="who-user">{safe}</div>')
 
 
def render_sources(sources) -> None:
    if not sources:
        return
 
    cards = []
 
    for i, source in enumerate(sources):
 
        metadata = source.get("metadata", {})
 
        name = html.escape(str(metadata.get("source", "Unknown paper")))
        page = html.escape(str(metadata.get("page", "?")))
        passage = html.escape(str(source.get("text", "")))
 
        cards.append(
            f"""
            <details class="source">
                <summary>
                    <span class="source-n">{i + 1}</span>
                    <span class="source-name">{name}</span>
                    <span class="source-page">Page {page}</span>
                    <span class="source-toggle">View retrieved passage</span>
                </summary>
                <div class="passage">{passage}</div>
            </details>
            """
        )
 
    md_html(
        f"""
        <div class="sources">
            <div class="sources-head">
                <span class="sources-title">Sources</span>
                <span class="sources-count">{len(sources)}</span>
            </div>
            {"".join(cards)}
        </div>
        """
    )
 
 
def render_meta(elapsed, sources) -> None:
    if elapsed is None:
        return
 
    count = len(sources) if sources else 0
    noun = "passage" if count == 1 else "passages"
 
    md_html(
        f'<div class="meta">Answered in {elapsed:.1f}s from {count} {noun}</div>'
    )
 
 
# ============================================================
# STATE AND INPUT
# ============================================================
 
if "messages" not in st.session_state:
    st.session_state.messages = []
 
question = st.chat_input("Ask a research question...")
 
if question:
    st.session_state.messages.append({"role": "user", "content": question})
 
 
# # ============================================================
# # SIDEBAR
# # ============================================================
 
# with st.sidebar:
 
#     md_html(
#         """
#         <div class="sidebar-brand">
#             <div class="sidebar-logo">📚</div>
#             <div>
#                 <div class="sidebar-title">Research AI</div>
#                 <div class="sidebar-subtitle">Local research assistant</div>
#             </div>
#         </div>
#         """
#     )
 
#     md_html('<div class="sidebar-section">Pipeline</div>')
 
#     md_html(
#         """
#         <div class="status-card">
#             <div class="status-row">
#                 <span class="status-label">Vector database</span>
#                 <span class="status-value">ChromaDB</span>
#             </div>
#             <div class="status-row">
#                 <span class="status-label">Embeddings</span>
#                 <span class="status-value">BGE</span>
#             </div>
#             <div class="status-row">
#                 <span class="status-label">Language model</span>
#                 <span class="status-value">GPT-OSS</span>
#             </div>
#         </div>
#         """
#     )
 
#     md_html('<div class="sidebar-section">Conversation</div>')
 
#     if st.button(
#         "🗑️  Clear conversation",
#         disabled=not st.session_state.messages,
#     ):
#         st.session_state.messages = []
#         st.rerun()
 
#     md_html('<div class="sidebar-section">About</div>')
 
#     md_html(
#         """
#         <div class="sidebar-info">
#             This assistant retrieves relevant passages from your indexed
#             research papers and uses them as context for each answer.
#             <br><br>
#             Every answer lists the papers and pages it drew on.
#         </div>
#         """
#     )
 
 
# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    md_html(
        """
        <div class="sidebar-brand">
            <div class="sidebar-logo">📚</div>
            <div>
                <div class="sidebar-title">Research AI</div>
                <div class="sidebar-subtitle">Local research assistant</div>
            </div>
        </div>
        """
    )

    # --------------------------------------------------------
    # PIPELINE
    # --------------------------------------------------------

    md_html('<div class="sidebar-section">Pipeline</div>')

    md_html(
        """
        <div class="status-card">
            <div class="status-row">
                <span class="status-label">Vector database</span>
                <span class="status-value">ChromaDB</span>
            </div>

            <div class="status-row">
                <span class="status-label">Embeddings</span>
                <span class="status-value">BGE</span>
            </div>

            <div class="status-row">
                <span class="status-label">Language model</span>
                <span class="status-value">GPT-OSS</span>
            </div>
        </div>
        """
    )

    # --------------------------------------------------------
    # ADD RESEARCH PAPERS
    # --------------------------------------------------------

    md_html('<div class="sidebar-section">Add Research Papers</div>')

    uploaded_files = st.file_uploader(
        "Upload PDF papers",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="Upload one or more research papers in PDF format."
    )

    if uploaded_files:

        os.makedirs("data/papers", exist_ok=True)

        for uploaded_file in uploaded_files:

            file_path = os.path.join(
                "data",
                "papers",
                uploaded_file.name
            )

            # Save PDF
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Ingest PDF
            with st.spinner(
                f"Indexing {uploaded_file.name}..."
            ):
                try:

                    ingest_pdf(file_path)

                    st.success(
                        f"✓ {uploaded_file.name} indexed"
                    )

                except Exception as e:

                    st.error(
                        f"Failed to index {uploaded_file.name}: {e}"
                    )

    # --------------------------------------------------------
    # CONVERSATION
    # --------------------------------------------------------

    md_html('<div class="sidebar-section">Conversation</div>')

    if st.button(
        "🗑️  Clear conversation",
        disabled=not st.session_state.messages,
    ):
        st.session_state.messages = []
        st.rerun()

    # --------------------------------------------------------
    # ABOUT
    # --------------------------------------------------------

    md_html('<div class="sidebar-section">About</div>')

    md_html(
        """
        <div class="sidebar-info">
            This assistant retrieves relevant passages from your indexed
            research papers and uses them as context for each answer.
            <br><br>
            Every answer lists the papers and pages it drew on.
        </div>
        """
    )
# ============================================================
# HEADER
# ============================================================
 
if not st.session_state.messages:
 
    md_html(
        """
        <div class="hero">
            <h1>Your research,<br>intelligently searchable.</h1>
            <div class="hero-sub">
                Ask questions about your research papers. Each answer comes
                with the papers and pages it was drawn from, and the exact
                passages behind it.
            </div>
            <div class="hero-hint">
                Try asking about methods, datasets, results, clinical
                findings, algorithms, or limitations.
            </div>
        </div>
        """
    )
 
else:
 
    md_html(
        """
        <div class="topbar">
            <span class="topbar-title">📚 Local Research Assistant</span>
            <span class="topbar-sub">Ask questions about your research papers.</span>
        </div>
        """
    )
 
 
# ============================================================
# CHAT HISTORY
# ============================================================
 
for message in st.session_state.messages:
 
    if message["role"] == "user":
 
        with st.chat_message("user", avatar=USER_AVATAR):
            render_user(message["content"])
 
    else:
 
        with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
            st.markdown(message["content"])
            render_sources(message.get("sources"))
            render_meta(message.get("elapsed"), message.get("sources"))
 
 
# ============================================================
# ANSWER A NEW QUESTION
# ============================================================
 
if question:
 
    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
 
        start = time.perf_counter()
 
        try:
            with st.spinner("Searching your research library..."):
                answer, sources = ask_question(question)
        except Exception as exc:
            st.error(f"Couldn't search your papers: {exc}")
            st.stop()
 
        elapsed = time.perf_counter() - start
 
        st.markdown(answer)
        render_sources(sources)
        render_meta(elapsed, sources)
 
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "elapsed": elapsed,
        }
    )