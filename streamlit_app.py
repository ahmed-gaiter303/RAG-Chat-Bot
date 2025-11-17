import os
from typing import List

import streamlit as st

from rag_engine import RAGEngine


# ---------- Page config ----------

st.set_page_config(
    page_title="RAG Talent & Docs Assistant · Ahmed Gaiter",
    layout="wide",
    page_icon="💼",
)


# ---------- Global UI CSS (neo-dark + glass) ----------

APP_CSS = """
<style>

/* Global background */
html, body, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 0% 0%, rgba(59,130,246,0.35), transparent 55%),
    radial-gradient(circle at 100% 100%, rgba(236,72,153,0.35), transparent 55%),
    #020617;
  color: #e5e7eb;
}

/* Main container */
.main .block-container {
  padding-top: 1.2rem;
  padding-bottom: 1.6rem;
  max-width: 1200px;
}

/* Sidebar shell */
[data-testid="stSidebar"] {
  background: transparent;
}

section[data-testid="stSidebar"] > div {
  background: rgba(15,23,42,0.96);
  backdrop-filter: blur(18px);
  border-radius: 20px;
  margin: 0.9rem 0.4rem 0.9rem 0.2rem;
  padding: 1.0rem 0.95rem 1.2rem 0.95rem;
  border: 1px solid rgba(148,163,184,0.5);
  box-shadow:
    0 18px 45px rgba(15,23,42,0.65),
    0 0 0 1px rgba(15,23,42,0.85);
}

section[data-testid="stSidebar"] {
  color: #e5e7eb;
}

/* File uploader */
[data-testid="stFileUploaderDropzone"] {
  background: rgba(15,23,42,0.96) !important;
  border-radius: 16px !important;
  border: 1px dashed rgba(148,163,184,0.85) !important;
  color: #e5e7eb !important;
}

[data-testid="stFileUploaderDropzone"] * {
  color: #e5e7eb !important;
}

/* Main shell */
.glass-shell {
  background: radial-gradient(circle at 0 0, rgba(56,189,248,0.18), transparent 55%),
              radial-gradient(circle at 100% 100%, rgba(251,113,133,0.18), transparent 55%),
              rgba(15,23,42,0.92);
  backdrop-filter: blur(18px);
  border-radius: 26px;
  padding: 1.4rem 1.6rem 1.6rem 1.6rem;
  border: 1px solid rgba(148,163,184,0.7);
  box-shadow:
    0 26px 70px rgba(15,23,42,0.95),
    0 0 0 1px rgba(15,23,42,0.85);
}

/* Top badge row */
.hero-kicker {
  font-size: 0.78rem;
  letter-spacing: 0.16em;
  color: #9ca3af;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}

/* Headings */
h1 {
  font-size: 2.1rem;
  letter-spacing: 0.02em;
  color: #f9fafb;
}

h2, h3 {
  color: #e5e7eb;
}

/* Stat cards */
.metric-card {
  padding: 0.7rem 0.9rem;
  border-radius: 16px;
  background: rgba(15,23,42,0.95);
  border: 1px solid rgba(55,65,81,0.9);
  box-shadow: 0 16px 40px rgba(15,23,42,0.85);
}

.metric-label {
  font-size: 0.78rem;
  color: #9ca3af;
}

.metric-value {
  font-size: 1.2rem;
  font-weight: 600;
  color: #f9fafb;
}

/* Quick action pills */
.qa-pill {
  border-radius: 999px;
  padding: 0.45rem 0.8rem;
  border: 1px solid rgba(148,163,184,0.85);
  background: linear-gradient(135deg, rgba(15,23,42,1), rgba(30,64,175,0.85));
  color: #e5e7eb;
  font-size: 0.78rem;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  box-shadow: 0 14px 32px rgba(15,23,42,0.85);
}

/* Tabs */
[data-baseweb="tab-list"] {
  gap: 0.4rem;
}
button[role="tab"] {
  border-radius: 999px !important;
}

/* Chat bubbles */
div[data-testid="stChatMessage"][data-testid*="user"] {
  background: linear-gradient(135deg, #4f46e5, #ec4899);
  color: #f9fafb;
  border-radius: 16px;
  border: none;
}

div[data-testid="stChatMessage"][data-testid*="assistant"] {
  background: rgba(15,23,42,0.95);
  color: #e5e7eb;
  border-radius: 16px;
  border: 1px solid rgba(55,65,81,0.9);
}

/* Chat input */
.stChatInputContainer {
  background: transparent;
  padding-top: 0.4rem;
}

div[data-testid="stChatInput"] textarea {
  background: rgba(15,23,42,0.98);
  border-radius: 14px;
  border: 1px solid rgba(55,65,81,0.95);
  padding: 0.75rem 0.9rem;
  color: #e5e7eb;
  box-shadow: 0 16px 40px rgba(15,23,42,0.95);
}

div[data-testid="stChatInput"] textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow:
    0 0 0 1px rgba(79,70,229,1),
    0 18px 46px rgba(55,65,81,1);
}

/* Sidebar buttons */
section[data-testid="stSidebar"] button {
  color: #e5e7eb !important;
  background-color: rgba(15,23,42,0.98) !important;
  border-radius: 999px !important;
  border: 1px solid rgba(75,85,99,0.95) !important;
  padding: 0.45rem 0.2rem;
  font-weight: 600;
  box-shadow: 0 16px 36px rgba(15,23,42,0.9);
  transition: all 0.12s ease-out;
}

section[data-testid="stSidebar"] button:not(:disabled):hover {
  background-color: rgba(37,99,235,0.95) !important;
  border-color: rgba(129,140,248,1) !important;
  color: #f9fafb !important;
  transform: translateY(-1px);
  box-shadow: 0 20px 48px rgba(30,64,175,1);
}

section[data-testid="stSidebar"] button:disabled {
  background-color: rgba(31,41,55,0.98) !important;
  color: #6b7280 !important;
  border: 1px solid rgba(55,65,81,0.95) !important;
  box-shadow: none !important;
}

/* Source badges */
.source-badge {
    display: inline-block;
    padding: 0.15rem 0.55rem;
    border-radius: 6px;
    background: rgba(15,23,42,0.98);
    color: #e5e7eb;
    font-size: 0.68rem;
    margin-right: 0.25rem;
    margin-top: 0.18rem;
    border: 1px solid rgba(55,65,81,0.95);
}

/* Lists */
ul.custom-list {
  padding-left: 1.1rem;
  color: #d1d5db;
}

ul.custom-list li {
  margin-bottom: 0.22rem;
}

/* Info alerts */
div.stAlert {
  background-color: rgba(30,64,175,0.18);
  color: #e5e7eb;
  border-radius: 12px;
  border: 1px solid rgba(129,140,248,0.9);
}

</style>
"""

st.markdown(APP_CSS, unsafe_allow_html=True)


# ---------- Session state ----------

if "rag" not in st.session_state:
    st.session_state.rag: RAGEngine = RAGEngine()
    st.session_state.index_built = False
    st.session_state.chat_history: List[dict] = []
    st.session_state.last_files = []
    st.session_state.chunks_count = 0
    st.session_state.questions_count = 0
    st.session_state.jd_path = None  # Job Description path

rag: RAGEngine = st.session_state.rag


# ---------- Sidebar: upload & controls ----------

with st.sidebar:
    st.markdown("#### 📂 Upload CV / Docs")
    uploaded_files = st.file_uploader(
        "PDF / TXT",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    st.caption("Max 200MB per file · All processing stays on your side.")

    if st.button("Load sample document", use_container_width=True):
        sample_path = "sample.txt"
        if not os.path.exists(sample_path):
            with open(sample_path, "w", encoding="utf-8") as f:
                f.write(
                    "Sample RAG document. This chatbot can answer questions "
                    "based on the text you upload. Add your documentation, "
                    "reports, or manuals here and ask anything about them."
                )
        st.success("Sample document created. Click 'Index documents' to use it.")

    file_paths = []
    if uploaded_files:
        for uf in uploaded_files:
            save_path = os.path.join("uploaded_" + uf.name)
            with open(save_path, "wb") as f:
                f.write(uf.getbuffer())
            file_paths.append(save_path)

    st.markdown("---")
    st.markdown("#### 📄 Job Description (optional)")
    jd_file = st.file_uploader(
        "JD PDF / TXT", type=["pdf", "txt"], key="jd_uploader"
    )
    if jd_file is not None:
        jd_save_path = os.path.join("uploaded_jd_" + jd_file.name)
        with open(jd_save_path, "wb") as f:
            f.write(jd_file.getbuffer())
        st.session_state.jd_path = jd_save_path
        st.caption(f"JD loaded: {jd_file.name}")

    st.markdown("---")

    if st.button("⚙️ Index documents", use_container_width=True):
        if not file_paths and not os.path.exists("sample.txt"):
            st.error("Please upload at least one document or load the sample.")
        else:
            if not file_paths and os.path.exists("sample.txt"):
                file_paths = ["sample.txt"]

            with st.spinner("Building embeddings index..."):
                try:
                    num_files, num_chunks = rag.build_index(file_paths)
                    st.session_state.index_built = True
                    st.session_state.last_files = file_paths
                    st.session_state.chunks_count = num_chunks
                    st.success(
                        f"Indexed {num_files} file(s) into {num_chunks} text chunks."
                    )
                except Exception as e:
                    st.session_state.index_built = False
                    st.error(f"Error while indexing: {e}")

    if st.button("🧹 Clear chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.questions_count = 0
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("#### 🤖 LLM status")
    if getattr(rag, "model", None) is None:
        st.caption("LLM not configured → bot returns the most relevant snippets only.")
    else:
        st.caption("Gemini configured → bot generates grounded, natural answers.")


# ---------- Header ----------

st.markdown(
    """
<div class="hero-kicker">
  RAG · TALENT & DOCUMENTS ASSISTANT
</div>
""",
    unsafe_allow_html=True,
)


st.markdown("<div class='glass-shell'>", unsafe_allow_html=True)

col_header_left, col_header_right = st.columns([3, 1], gap="large")

with col_header_left:
    st.markdown("## 💼 RAG Talent & Docs Assistant")
    st.markdown(
        "Turn CVs and documents into an interactive, AI‑powered knowledge base. "
        "Upload resumes, manuals, or PDFs and chat with them like a real assistant."
    )

with col_header_right:
    st.markdown(
        """
    <div style="display:flex; flex-direction:column; gap:0.4rem; align-items:flex-end;">
      <div style="
        padding:0.3rem 0.8rem;
        border-radius:999px;
        background:linear-gradient(135deg,#22c55e,#16a34a);
        color:#ecfdf5;
        font-size:0.75rem;
        box-shadow:0 12px 32px rgba(22,163,74,0.9);
      ">
        LIVE · DEMO READY
      </div>
      <div style="
        padding:0.25rem 0.75rem;
        border-radius:999px;
        border:1px solid rgba(148,163,184,0.85);
        background:rgba(15,23,42,0.96);
        font-size:0.72rem;
        color:#e5e7eb;
      ">
        Designed by Ahmed Gaiter
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# ---------- Metrics row ----------

m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(
        f"""
    <div class="metric-card">
      <div class="metric-label">Files indexed</div>
      <div class="metric-value">{len(st.session_state.last_files) if st.session_state.last_files else 0}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        f"""
    <div class="metric-card">
      <div class="metric-label">Chunks</div>
      <div class="metric-value">{st.session_state.chunks_count}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        f"""
    <div class="metric-card">
      <div class="metric-label">Questions this session</div>
      <div class="metric-value">{st.session_state.questions_count}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# ---------- Tabs ----------

tab_chat, tab_insights, tab_help = st.tabs(["💬 Chat", "📊 Insights", "ℹ️ How it works"])

quick_question = None

with tab_chat:
    # Quick actions row
    if st.session_state.index_built and st.session_state.last_files:
        qa_c1, qa_c2, qa_c3, qa_c4 = st.columns(4)
        with qa_c1:
            if st.button("📄 CV summary", use_container_width=True):
                quick_question = "Summarize this CV in 4 concise bullet points."
        with qa_c2:
            if st.button("🧠 Technical skills", use_container_width=True):
                quick_question = (
                    "List the main technical skills mentioned in this CV or document."
                )
        with qa_c3:
            if st.button("🎓 Certifications", use_container_width=True):
                quick_question = "What certifications and courses are mentioned?"
        with qa_c4:
            if st.button("🧾 Experience overview", use_container_width=True):
                quick_question = (
                    "Summarize the professional experience section in this CV."
                )

    left_col, right_col = st.columns([2.2, 1], gap="large")

    # ---------- Left: chat ----------

    with left_col:
        st.subheader("Chat console")

        if not st.session_state.index_built:
            st.info("Upload and index at least one document from the sidebar to start.")
        else:
            for msg in st.session_state.chat_history:
                with st.chat_message(
                    msg["role"],
                    avatar="🤖" if msg["role"] == "assistant" else "🧑",
                ):
                    st.markdown(msg["content"])

            user_input = quick_question or st.chat_input(
                "Ask a question about your CVs or documents..."
            )

            if user_input:
                st.session_state.questions_count += 1
                st.session_state.chat_history.append(
                    {"role": "user", "content": user_input}
                )

                with st.chat_message("user", avatar="🧑"):
                    st.markdown(user_input)

                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner(
                        "Retrieving relevant chunks and generating answer..."
                    ):
                        answer, retrieved = rag.answer(user_input)

                    st.markdown(answer)

                    if retrieved:
                        st.markdown("")
                        st.markdown("**Sources**")
                        for i, ch in enumerate(retrieved, start=1):
                            st.markdown(
                                f"<span class='source-badge'>[{i}] {ch.source}</span>",
                                unsafe_allow_html=True,
                            )

    # ---------- Right: analysis + export ----------

    with right_col:
        st.subheader("CV · JD analysis")

        cv_available = (
            st.session_state.last_files
            and len(st.session_state.last_files) == 1
            and st.session_state.index_built
        )
        jd_available = st.session_state.jd_path is not None

        if st.button(
            "🔍 Analyze CV vs JD",
            use_container_width=True,
            disabled=not (cv_available and jd_available),
        ):
            cv_path = st.session_state.last_files[0]
            with st.spinner("Analyzing CV against Job Description..."):
                analysis_text = rag.analyze_cv_vs_jd(cv_path, st.session_state.jd_path)
            st.markdown(analysis_text)

        if not (cv_available and jd_available):
            st.caption(
                "Upload exactly one CV and one Job Description to enable CV vs JD analysis."
            )

        st.markdown("---")
        st.subheader("Export report")

        if st.session_state.chat_history:
            report_lines = []
            for msg in st.session_state.chat_history:
                prefix = "User" if msg["role"] == "user" else "Assistant"
                report_lines.append(f"{prefix}: {msg['content']}")
                report_lines.append("")
            report_text = "\n".join(report_lines)

            st.download_button(
                "⬇️ Download chat report",
                data=report_text,
                file_name="chat_report.txt",
                mime="text/plain",
                use_container_width=True,
            )
        else:
            st.caption("Start a chat to enable report export.")


# ---------- Insights tab ----------

with tab_insights:
    st.subheader("Session insights")

    if st.session_state.index_built and st.session_state.last_files:
        st.markdown("**Indexed documents**")
        for fp in st.session_state.last_files:
            name = os.path.basename(fp)
            st.markdown(f"- {name}")

        if st.session_state.jd_path:
            st.markdown(f"- Job Description: {os.path.basename(st.session_state.jd_path)}")
    else:
        st.info("No indexed documents yet. Upload and index files from the sidebar.")

    st.markdown("---")
    st.markdown("**Engine summary**")
    st.markdown(
        """
- Retrieval: FAISS vector index on sentence-transformers embeddings.
- Generation: Gemini (if configured) with RAG grounding.
- Use cases: CV analysis, CV vs JD matching, document Q&A.
"""
    )


# ---------- Help / How it works tab ----------

with tab_help:
    st.subheader("How this assistant works")

    st.markdown(
        """
<ul class="custom-list">
<li>Upload one or more PDF/TXT files (CVs, manuals, reports) from the sidebar.</li>
<li>Optionally upload a Job Description to enable CV vs JD matching.</li>
<li>Click <b>Index documents</b> to build an embeddings-based vector index (FAISS).</li>
<li>Use quick action buttons (CV summary, skills, certifications) or ask your own questions.</li>
<li>The engine retrieves the most relevant chunks and calls Gemini to generate grounded answers.</li>
<li>You can export a full chat transcript as a text report from the Chat tab.</li>
</ul>
"""
    )

st.markdown("</div>", unsafe_allow_html=True)
