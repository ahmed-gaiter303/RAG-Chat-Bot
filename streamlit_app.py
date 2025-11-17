import os
from typing import List

import streamlit as st

from rag_engine import RAGEngine


# ---------- Page config & custom CSS ----------

st.set_page_config(page_title="RAG Chat Bot · Ahmed Gaiter", layout="wide")

GLASS_CSS = """
<style>

/* نجبر الخلفية تبقى فاتحة حتى لو المستخدم فعّل دارك مود */
html, body, [data-testid="stAppViewContainer"] {
  background:
    linear-gradient(135deg, rgba(79,70,229,0.14), transparent 55%),
    linear-gradient(315deg, rgba(236,72,153,0.12), transparent 55%),
    #F9FAFB !important;
  color: #111827 !important;
}

/* container أضيق شوية كأنه dashboard */
.main .block-container {
  padding-top: 1.4rem;
  padding-bottom: 1.5rem;
  max-width: 1120px;
}

/* سايدبار أبيض مسطّح بحافة واضحة */
[data-testid="stSidebar"] {
  background: transparent !important;
}

section[data-testid="stSidebar"] > div {
  background: #FFFFFF;
  border-radius: 16px;
  margin: 0.9rem 0.4rem 0.9rem 0.2rem;
  padding: 1rem 0.9rem 1.1rem 0.9rem;
  border: 1px solid rgba(209,213,219,0.9);
  box-shadow: 0 10px 30px rgba(15,23,42,0.08);
}

/* كارت رئيسي للشات شكل Dashboard card */
.glass-shell {
  background: #FFFFFF;
  border-radius: 20px;
  padding: 1.3rem 1.5rem 1.5rem 1.5rem;
  border: 1px solid rgba(209,213,219,0.95);
  box-shadow:
    0 18px 45px rgba(15,23,42,0.10),
    0 0 0 1px rgba(148,163,184,0.35);
}

/* شريط علوي داخل الكارت كأنه Product header + Pipeline ribbon */
.ribbon-bar {
  background: linear-gradient(90deg, #4f46e5, #ec4899);
  border-radius: 999px;
  padding: 0.45rem 0.9rem;
  display: inline-flex;
  gap: 0.45rem;
  align-items: center;
  color: #F9FAFB;
  font-size: 0.80rem;
  box-shadow: 0 10px 25px rgba(79,70,229,0.55);
}

.ribbon-chip {
  background: rgba(15,23,42,0.10);
  padding: 0.13rem 0.65rem;
  border-radius: 999px;
  border: 1px solid rgba(248,250,252,0.35);
}

/* نصوص */
h1 {
  font-size: 2.2rem;
  letter-spacing: 0.04em;
  color: #111827;
}

h2, h3 {
  color: #111827;
}

/* فقاعات الشات: user = card داكن، assistant = card فاتح */
div[data-testid="stChatMessage"][data-testid*="user"] {
  background: #111827;
  color: #F9FAFB;
  border-radius: 14px;
  border: none;
}

div[data-testid="stChatMessage"][data-testid*="assistant"] {
  background: #F3F4F6;
  color: #111827;
  border-radius: 14px;
  border: 1px solid rgba(209,213,219,0.9);
}

/* صندوق إدخال الشات */
.stChatInputContainer {
  background: transparent !important;
  padding-top: 0.6rem;
}

div[data-testid="stChatInput"] textarea {
  background: #FFFFFF;
  border-radius: 12px;
  border: 1px solid rgba(209,213,219,0.9);
  padding: 0.75rem 0.9rem;
  color: #111827;
  box-shadow: 0 12px 30px rgba(15,23,42,0.10);
}

div[data-testid="stChatInput"] textarea:focus {
  outline: none !important;
  border-color: #4F46E5;
  box-shadow: 0 0 0 1px rgba(79,70,229,0.85), 0 16px 36px rgba(79,70,229,0.25);
}

/* زر إرسال الأيقونة */
button[kind="primary"] svg {
  color: #F9FAFB !important;
}

/* أزرار السايدبار → مستطيلة داكنة */
section[data-testid="stSidebar"] button[kind="primary"] {
  border-radius: 10px;
  background: #111827;
  color: #F9FAFB;
  border: 0;
  padding: 0.45rem 0.2rem;
  font-weight: 600;
  box-shadow: 0 8px 20px rgba(15,23,42,0.45);
  transition: all 0.12s ease-out;
}

section[data-testid="stSidebar"] button[kind="primary"]:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 26px rgba(15,23,42,0.65);
}

/* Badges للمصادر */
.source-badge {
    display: inline-block;
    padding: 0.15rem 0.55rem;
    border-radius: 6px;
    background: #111827;
    color: #F9FAFB;
    font-size: 0.68rem;
    margin-right: 0.25rem;
    margin-top: 0.18rem;
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


# ---------- Header / Hero ----------

st.markdown(
    """
<div style="margin-bottom:0.6rem;">
  <div style="font-size:0.78rem; letter-spacing:0.18em; color:#6B7280; text-transform:uppercase; margin-bottom:0.25rem;">
    AHMED GAITER · RAG SUITE
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# ---------- Session state ----------

if "rag" not in st.session_state:
    st.session_state.rag: RAGEngine = RAGEngine()
    st.session_state.index_built = False
    st.session_state.chat_history: List[dict] = []
    st.session_state.last_files = []

rag: RAGEngine = st.session_state.rag


# ---------- Sidebar: Upload + Index + Controls ----------

with st.sidebar:
    st.markdown("#### Upload documents")
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

    if st.button("Index documents", use_container_width=True):
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

    if st.button("Clear chat history", use_container_width=True):
        st.session_state.chat_history = []
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("#### LLM status")
    if rag.llm_client is None:
        st.caption("OPENAI_API_KEY not set → bot returns the most relevant snippets only.")
    else:
        st.caption("OpenAI configured → bot generates natural answers grounded in your docs.")


# ---------- Main card with ribbon ----------

st.markdown("<div class='glass-shell'>", unsafe_allow_html=True)

st.markdown(
    """
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
  <div>
    <h1 style="margin:0;">RAG Chat Bot</h1>
    <p style="margin:0.25rem 0 0; font-size:0.93rem; color:#4B5563; max-width:520px;">
      Chat interface for your PDFs and text documents. Upload, index, and query your knowledge base with a clean, product-ready dashboard UI.
    </p>
  </div>
  <div class="ribbon-bar">
    <span>RAG PIPELINE</span>
    <span class="ribbon-chip">Upload</span>
    <span class="ribbon-chip">Index</span>
    <span class="ribbon-chip">Query</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

left_col, right_col = st.columns([2.2, 1], gap="large")


# ---------- Left column: Chat ----------

with left_col:
    st.subheader("CHAT · CONSOLE")

    if not st.session_state.index_built:
        st.info("Please upload and index documents first from the sidebar.")
    else:
        for msg in st.session_state.chat_history:
            with st.chat_message(
                msg["role"],
                avatar="ＡＩ" if msg["role"] == "assistant" else "ＵＳＲ",
            ):
                st.markdown(msg["content"])

        user_input = st.chat_input("Ask a question about your documents...")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            with st.chat_message("user", avatar="ＵＳＲ"):
                st.markdown(user_input)

            with st.chat_message("assistant", avatar="ＡＩ"):
                with st.spinner("Retrieving relevant chunks and generating answer..."):
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

            st.experimental_rerun()


# ---------- Right column: Info ----------

with right_col:
    st.subheader("SESSION · STATUS")

    if st.session_state.index_built and st.session_state.last_files:
        st.markdown(f"- **Files indexed:** {len(st.session_state.last_files)}")
        st.markdown("- **Vector index:** FAISS (L2 distance)")
    else:
        st.markdown("- **Files indexed:** 0")
        st.markdown("- **Vector index:** not built yet")

    st.markdown("---")
    st.subheader("FLOW · PIPELINE")
    st.markdown(
        """
<ul class="custom-list">
<li>Upload one or more PDF/TXT files from the sidebar.</li>
<li>Click <b>Index documents</b> to build the vector index with embeddings.</li>
<li>Ask questions in the chat console on the left.</li>
<li>The engine retrieves the most relevant chunks and (optionally) calls OpenAI to answer.</li>
</ul>
""",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.subheader("USAGE · NOTES")
    st.markdown(
        """
<ul class="custom-list">
<li>Use clear questions like <i>“Summarize chapter 2”</i> أو <i>“What are the key points about feature X?”</i>.</li>
<li>Upload multiple files لبناء base معرفة أعمق.</li>
<li>في الإنتاج، يمكن توصيل هذه الواجهة بوثائق الشركة أو وثائق العملاء كـ branded assistant.</li>
</ul>
""",
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)
