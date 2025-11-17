import os
from typing import List

import streamlit as st

from rag_engine import RAGEngine


# ---------- Page config & premium glass UI ----------

st.set_page_config(page_title="RAG Chat Bot · Premium", layout="wide")

GLASS_CSS = """
<style>

/* خلفية فاتحة هلامية (glassmorphism) */
body {
  background:
    radial-gradient(circle at 0% 0%, rgba(129,140,248,0.20), transparent 55%),
    radial-gradient(circle at 100% 0%, rgba(236,72,153,0.18), transparent 55%),
    radial-gradient(circle at 0% 100%, rgba(45,212,191,0.18), transparent 55%),
    #F3F4F6;
}

/* تقليل الـ padding وتوسيط المحتوى */
.main .block-container {
  padding-top: 1.2rem;
  padding-bottom: 1.5rem;
  max-width: 1180px;
}

/* سايدبار زجاجي أبيض */
[data-testid="stSidebar"] {
  background: transparent;
}

section[data-testid="stSidebar"] > div {
  background: rgba(255,255,255,0.85);
  border-radius: 24px;
  margin: 0.8rem 0.4rem 0.8rem 0.2rem;
  padding: 1.1rem 1rem 1.3rem 1rem;
  border: 1px solid rgba(148,163,184,0.50);
  box-shadow: 0 24px 55px rgba(15,23,42,0.12);
  backdrop-filter: blur(22px) saturate(160%);
}

/* كارت زجاجي رئيسي للشات */
.glass-shell {
  background:
    radial-gradient(circle at 0% 0%, rgba(129,140,248,0.18), transparent 55%),
    radial-gradient(circle at 100% 100%, rgba(244,114,182,0.18), transparent 55%),
    rgba(255,255,255,0.92);
  border-radius: 28px;
  padding: 1.4rem 1.6rem 1.6rem 1.6rem;
  border: 1px solid rgba(226,232,240,0.95);
  box-shadow: 0 28px 70px rgba(15,23,42,0.20);
  backdrop-filter: blur(26px) saturate(170%);
}

/* عناوين واضحة غامقة */
h1, h2, h3 {
  color: #0F172A;
  font-weight: 700;
}

/* فقاعات الشات - مستخدم */
div[data-testid="stChatMessage"][data-testid*="user"] {
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  color: #F9FAFB;
  border-radius: 18px;
  border: none;
}

/* فقاعات الشات - بوت */
div[data-testid="stChatMessage"][data-testid*="assistant"] {
  background: rgba(248,250,252,0.95);
  border-radius: 18px;
  border: 1px solid rgba(203,213,225,0.9);
}

/* صندوق إدخال الشات */
.stChatInputContainer {
  background: transparent !important;
  padding-top: 0.6rem;
}

div[data-testid="stChatInput"] textarea {
  background: rgba(255,255,255,0.98);
  border-radius: 999px;
  border: 1px solid rgba(209,213,219,0.9);
  padding: 0.75rem 1rem;
  color: #0F172A;
  box-shadow: 0 0 0 1px rgba(148,163,184,0.35), 0 16px 38px rgba(15,23,42,0.18);
}

div[data-testid="stChatInput"] textarea:focus {
  outline: none !important;
  border-color: #6366F1;
  box-shadow: 0 0 0 1px rgba(99,102,241,0.9), 0 18px 45px rgba(79,70,229,0.25);
}

/* زرار الشات (أيقونة الإرسال) */
button[kind="primary"] svg {
  color: #F9FAFB !important;
}

/* أزرار سايدبار بشكل Jelly */
section[data-testid="stSidebar"] button[kind="primary"] {
  border-radius: 999px;
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  color: #f9fafb;
  border: 0;
  padding: 0.45rem 0.2rem;
  font-weight: 600;
  box-shadow: 0 10px 24px rgba(79,70,229,0.55);
  transition: all 0.15s ease-out;
}

section[data-testid="stSidebar"] button[kind="primary"]:hover {
  transform: translateY(-1px) scale(1.01);
  box-shadow: 0 14px 32px rgba(79,70,229,0.65);
  filter: saturate(120%);
}

/* Badges للمصادر */
.source-badge {
    display: inline-block;
    padding: 0.18rem 0.55rem;
    border-radius: 999px;
    background: rgba(15,23,42,0.05);
    color: #111827;
    font-size: 0.70rem;
    margin-right: 0.25rem;
    margin-top: 0.18rem;
    border: 1px solid rgba(148,163,184,0.9);
}

/* قوائم How it works / Tips */
ul.custom-list {
  padding-left: 1.1rem;
  color: #374151;
}

ul.custom-list li {
  margin-bottom: 0.22rem;
}

</style>
"""


st.markdown(GLASS_CSS, unsafe_allow_html=True)


# ---------- Hero (العنوان + السطر التسويقي) ----------

st.markdown(
    """
<div style="text-align:center; margin-top:0.4rem; margin-bottom:1.1rem;">
  <h1 style="
      font-size:2.4rem;
      margin-bottom:0.35rem;
      background: linear-gradient(120deg, #4f46e5, #ec4899);
      -webkit-background-clip:text;
      color: transparent;
  ">
    RAG Chat Bot
  </h1>

  <p style="font-size:1rem; color:#4B5563; max-width:740px; margin:auto;">
    Premium AI assistant that reads your PDF & text documents, understands them, and answers questions instantly.
    Designed with a modern glassmorphism interface for your portfolio and real-world clients.
  </p>

  <div style="margin-top:0.9rem; display:inline-flex; gap:0.4rem; flex-wrap:wrap; justify-content:center;">
    <span style="background:#EEF2FF; color:#3730A3; padding:0.25rem 0.75rem; border-radius:999px; font-size:0.82rem;">
      📂 Upload · 🔍 Index · 💬 Ask
    </span>
    <span style="background:#ECFEFF; color:#0F766E; padding:0.25rem 0.75rem; border-radius:999px; font-size:0.82rem;">
      Built with Python · Streamlit · FAISS
    </span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)



# ---------- تحضير الـ session state ----------

if "rag" not in st.session_state:
    st.session_state.rag: RAGEngine = RAGEngine()
    st.session_state.index_built = False
    st.session_state.chat_history: List[dict] = []
    st.session_state.last_files = []

rag: RAGEngine = st.session_state.rag


# ---------- Sidebar: Upload + Index + Controls ----------

with st.sidebar:
    st.markdown("### 📂 Upload documents")
    uploaded_files = st.file_uploader(
        "Drag and drop PDF / TXT",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    st.caption("Max 200MB per file · All processing stays on your side.")

    if st.button("📄 Load sample document", use_container_width=True):
        sample_path = "sample.txt"
        if not os.path.exists(sample_path):
            with open(sample_path, "w", encoding="utf-8") as f:
                f.write(
                    "Sample RAG document. This chatbot can answer questions "
                    "based on the text you upload. Add your documentation, "
                    "reports, or manuals here and ask anything about them."
                )
        st.success("Sample document created. Click **Index documents** to use it.")

    file_paths = []
    if uploaded_files:
        for uf in uploaded_files:
            save_path = os.path.join("uploaded_" + uf.name)
            with open(save_path, "wb") as f:
                f.write(uf.getbuffer())
            file_paths.append(save_path)

    st.markdown("---")

    if st.button("⚙️ Index documents", use_container_width=True):
        if not file_paths and not os.path.exists("sample.txt"):
            st.error("Please upload at least one document or load the sample.")
        else:
            if not file_paths and os.path.exists("sample.txt"):
                file_paths = ["sample.txt"]

            with st.spinner("Indexing documents with embeddings & FAISS..."):
                try:
                    num_files, num_chunks = rag.build_index(file_paths)
                    st.session_state.index_built = True
                    st.session_state.last_files = file_paths
                    st.success(f"Indexed {num_files} files into {num_chunks} text chunks.")
                except Exception as e:
                    st.session_state.index_built = False
                    st.error(f"Error while indexing: {e}")

    if st.button("🧹 Clear chat history", use_container_width=True):
        st.session_state.chat_history = []
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("### 🔐 LLM status")
    if rag.llm_client is None:
        st.caption("OPENAI_API_KEY not set → bot returns the most relevant snippets only.")
    else:
        st.caption("OpenAI configured → bot generates natural answers grounded in your docs.")


# ---------- Main glass card layout ----------

st.markdown("<div class='glass-shell'>", unsafe_allow_html=True)

left_col, right_col = st.columns([2.2, 1], gap="large")

with left_col:
    st.subheader("💬 Chat")

    if not st.session_state.index_built:
        st.info("Please upload and index documents first from the sidebar.")
    else:
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                with st.chat_message(
                    msg["role"], avatar="🤖" if msg["role"] == "assistant" else "🧑"
                ):
                    st.markdown(msg["content"])

        user_input = st.chat_input("Ask a question about your documents...")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            with st.chat_message("user", avatar="🧑"):
                st.markdown(user_input)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Retrieving relevant chunks and generating answer..."):
                    answer, retrieved = rag.answer(user_input)

                st.markdown(answer)

                if retrieved:
                    st.markdown("")
                    st.markdown("**Sources**:")
                    for i, ch in enumerate(retrieved, start=1):
                        st.markdown(
                            f"<span class='source-badge'>[{i}] {ch.source}</span>",
                            unsafe_allow_html=True,
                        )

            st.experimental_rerun()

with right_col:
    st.subheader("📊 Session info")

    if st.session_state.index_built and st.session_state.last_files:
        st.markdown(f"- **Files indexed:** {len(st.session_state.last_files)}")
        st.markdown("- **Vector index:** FAISS (L2 distance)")
    else:
        st.markdown("- **Files indexed:** 0")
        st.markdown("- **Vector index:** not built yet")

    st.markdown("---")
    st.markdown("### 🧠 How it works")
    st.markdown(
        """
<ul class="custom-list">
<li>Upload one or more PDF/TXT files from the sidebar.</li>
<li>Click <b>Index documents</b> to build the vector index with embeddings.</li>
<li>Ask questions in the chat box on the left.</li>
<li>The bot retrieves the most relevant chunks and (optionally) uses OpenAI to answer.</li>
</ul>
""",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown(
        """
<ul class="custom-list">
<li>Use clear questions like <i>“Summarize section X”</i> or <i>“What are the key points about Y?”</i>.</li>
<li>Upload multiple files to build a richer knowledge base.</li>
<li>For clients, plug this engine into their internal docs to create a branded AI assistant.</li>
</ul>
""",
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

