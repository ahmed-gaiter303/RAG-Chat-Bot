# streamlit_app.py
import os
from typing import List

import streamlit as st

from rag_engine import RAGEngine


# ---------- Page config & custom CSS ----------

st.set_page_config(page_title="RAG Chat Bot", layout="wide")

st.markdown(
    """
<style>
/* Remove top padding */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
}

/* Chat input background */
.stChatInputContainer {
    background: #050816 !important;
}

/* Source badges */
.source-badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    background-color: #1A202C;
    color: #E2E8F0;
    font-size: 0.70rem;
    margin-right: 0.25rem;
    margin-top: 0.15rem;
    border: 1px solid #4C51BF55;
}
</style>
""",
    unsafe_allow_html=True,
)


# ---------- Hero section ----------

st.markdown(
    """
<div style="text-align:center; margin-top:0.2rem; margin-bottom:1.5rem;">
  <h1 style="font-size:2.6rem; margin-bottom:0.3rem;">🤖 RAG Chat Bot</h1>
  <p style="font-size:1.05rem; color:#A0AEC0; max-width:720px; margin:auto;">
    AI assistant that reads your PDF and text documents, understands them,
    and answers questions instantly – perfect for documentation, reports, and knowledge bases.
  </p>
  <div style="margin-top:0.8rem;">
    <span style="background:#1A202C; color:#CBD5F5; padding:0.3rem 0.7rem;
                 border-radius:999px; font-size:0.85rem; margin-right:0.4rem;">
      📂 Upload → 🔍 Index → 💬 Ask
    </span>
    <span style="background:#171923; color:#9F7AEA; padding:0.3rem 0.7rem;
                 border-radius:999px; font-size:0.85rem;">
      Built with Streamlit · SentenceTransformers · FAISS
    </span>
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
    st.session_state.doc_text_preview = ""


rag: RAGEngine = st.session_state.rag


# ---------- Sidebar: Upload & indexing ----------

with st.sidebar:
    st.header("📁 Upload Documents")

    uploaded_files = st.file_uploader(
        "Drag and drop PDF or TXT files",
        type=["pdf", "txt"],
        accept_multiple_files=True,
    )

    st.markdown(
        "<small style='color:#A0AEC0;'>Max 200MB per file · PDF, TXT</small>",
        unsafe_allow_html=True,
    )

    # Optional sample
    if st.button("📄 Load sample document"):
        sample_path = "sample.txt"
        if not os.path.exists(sample_path):
            with open(sample_path, "w", encoding="utf-8") as f:
                f.write(
                    "Sample RAG document. This chatbot can answer questions "
                    "based on the text you upload. Add your documentation, "
                    "reports, or manuals here and ask anything about them."
                )
        st.success("Sample document created. Please click 'Index documents'.")

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

            with st.spinner("Indexing documents..."):
                try:
                    num_files, num_chunks = rag.build_index(file_paths)
                    st.session_state.index_built = True
                    st.session_state.last_files = file_paths
                    st.success(f"Indexed {num_files} files into {num_chunks} chunks.")
                except Exception as e:
                    st.session_state.index_built = False
                    st.error(f"Error while indexing: {e}")

    if st.button("🧹 Clear chat history", use_container_width=True):
        st.session_state.chat_history = []
        st.experimental_rerun()

    st.markdown("---")

    st.markdown("### ⚙️ LLM status")
    if rag.llm_client is None:
        st.caption(
            "🔒 OPENAI_API_KEY not set – bot will return relevant snippets only."
        )
    else:
        st.caption("✅ OpenAI configured – bot will generate natural answers.")


# ---------- Layout: main content ----------

left_col, right_col = st.columns([2.2, 1], gap="large")

with left_col:
    st.subheader("💬 Chat")

    if not st.session_state.index_built:
        st.info("Please upload and index documents first from the sidebar.")
    else:
        # Show chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(
                msg["role"], avatar="🤖" if msg["role"] == "assistant" else "🧑"
            ):
                st.markdown(msg["content"])

        user_input = st.chat_input("Ask a question about your documents...")

        if user_input:
            # Add user message
            st.session_state.chat_history.append(
                {"role": "user", "content": user_input}
            )

            with st.chat_message("user", avatar="🧑"):
                st.markdown(user_input)

            # Get answer
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Thinking with your documents..."):
                    answer, retrieved = rag.answer(user_input)

                st.markdown(answer)

                # Show sources as badges
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
        st.markdown(f"- **Vector index:** FAISS (L2)")
    else:
        st.markdown("- **Files indexed:** 0")
        st.markdown("- **Vector index:** not built yet")

    st.markdown("---")
    st.markdown("### 🧠 How it works")
    st.markdown(
        """
1. Upload one or more PDF/TXT files from the sidebar.  
2. Click **'Index documents'** to build the vector index.  
3. Ask questions in the chat box on the left.  
4. The bot retrieves the most relevant chunks and (optionally) uses OpenAI to answer.  
"""
    )

    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown(
        """
- Use clear questions like *\"Summarize section X\"* or *\"What are the key points about Y?\"*.  
- Upload multiple files to build a small knowledge base.  
- For production, plug this engine into your internal docs or client knowledge base.  
"""
    )
