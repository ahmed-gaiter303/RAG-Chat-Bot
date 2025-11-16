import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

load_dotenv()

class RAGBot:
    def __init__(self):
        self.documents = []
    
    def load_documents(self, file_paths):
        documents = []
        for file_path in file_paths:
            try:
                if file_path.endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    if docs:
                        documents.extend(docs)
                elif file_path.endswith('.txt'):
                    loader = TextLoader(file_path)
                    docs = loader.load()
                    if docs:
                        documents.extend(docs)
            except Exception as e:
                print(f"Error: {e}")
                continue
        self.documents = documents
        return documents
    
    def create_vector_store(self, documents):
        if not documents:
            raise Exception("No documents!")
        self.documents = documents
    
    def ask(self, question):
        if not self.documents:
            return "Load documents first!"
        
        question_words = question.lower().split()
        best_match = None
        best_score = 0
        
        for doc in self.documents:
            content = doc.page_content.lower()
            score = sum(1 for word in question_words if word in content)
            if score > best_score:
                best_score = score
                best_match = doc.page_content
        
        if best_match:
            return f"Found in your documents:\n\n{best_match[:500]}...\n\n(Based on keyword search)"
        else:
            return "No matching information found. Try different keywords."
    
    def save_vector_store(self, path="vector_store"):
        pass
    
    def load_vector_store(self, path="vector_store"):
        pass
