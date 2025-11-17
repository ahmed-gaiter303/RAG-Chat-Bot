# rag_engine.py
import os
import uuid
from dataclasses import dataclass
from typing import List, Tuple, Optional

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()


@dataclass
class DocumentChunk:
    id: str
    source: str
    content: str


class RAGEngine:
    """
    Simple RAG engine:
    - Load PDF/TXT files
    - Split into chunks
    - Build FAISS index with sentence-transformers embeddings
    - Retrieve top-k chunks
    - Optionally call OpenAI to generate an answer
    """

    def __init__(self):
        # Model for embeddings
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")

        # Vector index + storage
        self.index = None
        self.chunks: List[DocumentChunk] = []

        # Optional LLM via OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            from openai import OpenAI
            self.llm_client = OpenAI(api_key=self.openai_api_key)
        else:
            self.llm_client = None

    # ---------- Loading & chunking ----------

    def load_txt(self, path: str) -> str:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def load_pdf(self, path: str) -> str:
        reader = PdfReader(path)
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        return "\n".join(texts)

    def load_documents(self, paths: List[str]) -> str:
        """Return full combined text (for stats)"""
        combined = []
        for p in paths:
            ext = os.path.splitext(p)[1].lower()
            try:
                if ext == ".txt":
                    combined.append(self.load_txt(p))
                elif ext == ".pdf":
                    combined.append(self.load_pdf(p))
            except Exception as e:
                print(f"Error loading {p}: {e}")
        return "\n".join(combined)

    def _split_text(self, text: str, chunk_size: int = 700, overlap: int = 150) -> List[str]:
        """Simple recursive splitter based on characters."""
        text = text.replace("\r", " ").replace("\n\n", "\n")
        chunks = []
        start = 0
        length = len(text)

        while start < length:
            end = min(start + chunk_size, length)
            chunk = text[start:end]

            # try to cut at last period
            last_period = chunk.rfind(".")
            if last_period != -1 and end != length:
                end = start + last_period + 1
                chunk = text[start:end]

            chunks.append(chunk.strip())
            start = max(end - overlap, end)

        return [c for c in chunks if c]

    def build_index(self, file_paths: List[str]) -> Tuple[int, int]:
        """Load docs, split to chunks, embed, and build FAISS index."""
        self.chunks = []
        all_text = ""

        for path in file_paths:
            ext = os.path.splitext(path)[1].lower()
            if ext not in [".pdf", ".txt"]:
                continue

            try:
                if ext == ".pdf":
                    content = self.load_pdf(path)
                else:
                    content = self.load_txt(path)
            except Exception as e:
                print(f"Error reading {path}: {e}")
                continue

            all_text += content + "\n"
            split_chunks = self._split_text(content)

            for c in split_chunks:
                self.chunks.append(
                    DocumentChunk(
                        id=str(uuid.uuid4()),
                        source=os.path.basename(path),
                        content=c,
                    )
                )

        if not self.chunks:
            raise ValueError("No chunks created from the provided documents.")

        # Embed all chunks
        texts = [c.content for c in self.chunks]
        embeddings = self.embed_model.encode(texts, show_progress_bar=False)
        embeddings = np.asarray(embeddings).astype("float32")

        # Build FAISS index
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        return len(file_paths), len(self.chunks)

    # ---------- Retrieval & answer ----------

    def retrieve(self, query: str, k: int = 4) -> List[DocumentChunk]:
        if self.index is None or not self.chunks:
            raise ValueError("Index is not built yet.")

        q_emb = self.embed_model.encode([query]).astype("float32")
        distances, indices = self.index.search(q_emb, k)

        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self.chunks):
                results.append(self.chunks[idx])
        return results

    def _build_prompt(self, query: str, retrieved: List[DocumentChunk]) -> str:
        context = "\n\n".join(
            [f"[{i+1}] From {c.source}:\n{c.content}" for i, c in enumerate(retrieved)]
        )

        prompt = f"""
You are an AI assistant that answers questions based strictly on the provided context.
If the answer is not clearly contained in the context, say you are not sure.

Context:
{context}

Question: {query}

Answer in a clear, concise paragraph and, if helpful, bullet points.
Mention which source snippets you used like [1], [2] etc.
"""
        return prompt.strip()

    def answer(self, query: str) -> Tuple[str, List[DocumentChunk]]:
        """Return answer text and retrieved chunks."""
        if self.index is None:
            return "Please upload and index documents first.", []

        retrieved = self.retrieve(query)

        # If no LLM, fallback: show snippets only
        if self.llm_client is None:
            snippet_texts = "\n\n---\n\n".join(
                [f"From {c.source}:\n{c.content}" for c in retrieved]
            )
            answer = (
                "LLM API key is not configured, so here are the most relevant passages "
                "from your documents:\n\n" + snippet_texts
            )
            return answer, retrieved

        # With OpenAI LLM
        prompt = self._build_prompt(query, retrieved)

        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful RAG assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"Error contacting LLM: {e}"

        return answer, retrieved
