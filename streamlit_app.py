import streamlit as st
import os
from rag_bot import RAGBot
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="RAG Chat Bot", layout="wide")
st.title("🤖 RAG Chat Bot")
st.markdown("---")

# Initialize session state properly
if "bot" not in st.session_state:
    st.session_state.bot = None
    st.session_state.chat_history = []
    st.session_state.loaded = False

# Initialize bot only once
if st.session_state.bot is None:
    try:
        st.session_state.bot = RAGBot()
    except Exception as e:
        st.error(f"Error initializing bot: {str(e)}")
        st.stop()

with st.sidebar:
    st.header("📁 Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF or TXT files", 
        type=["pdf", "txt"], 
        accept_multiple_files=True
    )
    
    if uploaded_files and len(uploaded_files) > 0:
        if st.button("📚 Load Documents", use_container_width=True):
            with st.spinner("Processing documents..."):
                try:
                    file_paths = []
                    for file in uploaded_files:
                        file_path = f"/tmp/{file.name}"
                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())
                        file_paths.append(file_path)
                    
                    documents = st.session_state.bot.load_documents(file_paths)
                    
                    if not documents:
                        st.error("❌ No documents found!")
                    else:
                        st.session_state.bot.create_vector_store(documents)
                        st.session_state.loaded = True
                        st.success(f"✅ Loaded {len(documents)} documents!")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

if st.session_state.loaded:
    st.subheader("💬 Chat")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get response
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.bot.ask(prompt)
            except Exception as e:
                response = f"Error: {str(e)}"
        
        # Add assistant message
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        with st.chat_message("assistant"):
            st.write(response)
else:
    st.info("📤 Please upload documents first!")
