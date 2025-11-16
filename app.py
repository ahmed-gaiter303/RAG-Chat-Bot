import streamlit as st
import os
from rag_bot import RAGBot
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="RAG Chat Bot", layout="wide")
st.title("🤖 RAG Chat Bot")
st.markdown("---")

# Initialize session state
if "bot" not in st.session_state:
    st.session_state.bot = RAGBot()
    st.session_state.chat_history = []
    st.session_state.loaded = False

# Sidebar
with st.sidebar:
    st.header("📁 Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF or TXT files",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        file_paths = []
        for file in uploaded_files:
            # Save file temporarily
            with open(file.name, "wb") as f:
                f.write(file.getbuffer())
            file_paths.append(file.name)
        
        if st.button("📚 Load Documents", use_container_width=True):
            with st.spinner("Processing documents..."):
                try:
                    documents = st.session_state.bot.load_documents(file_paths)
                    
                    if not documents:
                        st.error("❌ No documents found! Make sure the PDF/TXT is readable.")
                    else:
                        st.session_state.bot.create_vector_store(documents)
                        st.session_state.bot.save_vector_store()
                        st.session_state.loaded = True
                        st.success(f"✅ Loaded {len(documents)} documents!")
                except Exception as e:
                    st.error(f"❌ Error loading documents: {str(e)}")

# Main chat area
if st.session_state.loaded:
    # Chat history
    st.subheader("💬 Chat History")
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Input
    user_input = st.chat_input("Ask a question about your documents...")
    
    if user_input:
        # Add to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get response
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.bot.ask(user_input)
            except Exception as e:
                response = f"Error: {str(e)}"
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
        
        st.rerun()
else:
    st.info("📤 Please upload documents first to get started!")
