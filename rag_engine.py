import os
import textwrap
from typing import List, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import google.generativeai as genai


class RetrievedChunk:
    def __init__(self, content: str, source: str):
        self.content = content
        self.source = source


class RAGEngine:
    def __init__(self, embedding_dim: int = 384):
        """
        RAG engine:
        - Reads PDF and TXT files.
        - Builds a FAISS index using sentence-transformers embeddings.
        - Uses Gemini for answer generation when configured.
        """
        # Embedding model
        self.embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.embedding_dim = embedding_dim

        # Gemini configuration
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
        else:
            self.model = None

        self.index = None
        self.chunks: List[RetrievedChunk] = []

    # ---------- File reading ---------- #

    def _read_txt(self, path: str) -> str:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _read_pdf(self, path: str) -> str:
        reader = PdfReader(path)
        pages_text = []
        for page in reader.pages:
            try:
                t = page.extract_text() or ""
            except Exception:
                t = ""
            pages_text.append(t)
        return "\n".join(pages_text)

    def _load_file_text(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".txt":
            return self._read_txt(path)
        elif ext == ".pdf":
            return self._read_pdf(path)
        else:
            return ""

    # ---------- Embeddings ---------- #

    def _embed_text(self, texts: List[str]) -> np.ndarray:
        """
        Convert a list of texts into an embeddings matrix (n x d).
        """
        embs = self.embed_model.encode(
            texts, convert_to_numpy=True, show_progress_bar=False
        )
        embs = embs.astype("float32")
        return embs

    # ---------- Index building ---------- #

    def build_index(self, file_paths: List[str]) -> Tuple[int, int]:
        """
        Read files, split them into chunks, and build a FAISS index.
        Returns: (number_of_files, number_of_chunks).
        """
        all_chunks: List[RetrievedChunk] = []

        for path in file_paths:
            if not os.path.exists(path):
                continue

            raw_text = self._load_file_text(path)
            if not raw_text.strip():
                continue

            # Normalize text
            text = raw_text.replace("\r", "\n")
            text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

            # Chunking with small overlap
            chunk_size = 500  # characters
            overlap = 100
            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk = text[start:end].strip()
                if chunk:
                    all_chunks.append(
                        RetrievedChunk(
                            content=chunk, source=os.path.basename(path)
                        )
                    )
                start = end - overlap

        if not all_chunks:
            self.index = None
            self.chunks = []
            return len(file_paths), 0

        texts = [c.content for c in all_chunks]
        embs = self._embed_text(texts)

        index = faiss.IndexFlatL2(self.embedding_dim)
        index.add(embs)

        self.index = index
        self.chunks = all_chunks

        return len(file_paths), len(all_chunks)

    # ---------- Retrieval ---------- #

    def _retrieve(self, query: str, top_k: int = 5) -> List[RetrievedChunk]:
        if self.index is None or not self.chunks:
            return []

        q_emb = self._embed_text([query])
        distances, indices = self.index.search(q_emb, top_k)

        retrieved: List[RetrievedChunk] = []
        for idx in indices[0]:
            if 0 <= idx < len(self.chunks):
                retrieved.append(self.chunks[idx])

        return retrieved

    # ---------- Generic QA ---------- #

    def answer(self, query: str) -> Tuple[str, List[RetrievedChunk]]:
        """
        Main QA entrypoint used by the Streamlit app.
        Returns (answer_text, retrieved_chunks).
        """
        retrieved = self._retrieve(query)

        if not retrieved:
            return (
                "No relevant passages were found in your documents for this question.",
                [],
            )

        # No LLM: just return snippets
        if self.model is None:
            text = "Here are the most relevant passages from your documents:\n\n"
            for i, ch in enumerate(retrieved, start=1):
                text += f"[{i}] {ch.content}\n\n"
            return text, retrieved

        context_blocks = []
        for i, ch in enumerate(retrieved, start=1):
            context_blocks.append(f"[{i}] {ch.content}")
        context_text = "\n\n".join(context_blocks)

        prompt = textwrap.dedent(
            f"""
            You are an AI assistant that answers questions based only on the passages below.

            User question:
            {query}

            Retrieved passages:
            {context_text}

            Instructions:
            - Use the information in the passages as your primary source.
            - You may use light logical inference, but do not hallucinate facts not supported by the text.
            - If the question is about a CV (resume), you may extract:
              * Professional summary.
              * Roles, job titles, companies, and dates.
              * Technical skills.
              * Certifications.
            - Only say that information is not available if there is truly nothing related to the question.
            - Answer in the same language used by the user (Arabic or English).
            - Keep the answer clear and concise, and use numbered or bulleted lists when helpful.
            """
        )

        try:
            resp = self.model.generate_content(prompt)
            answer_text = resp.text.strip() if resp and resp.text else (
                "Gemini did not return any content."
            )
        except Exception:
            answer_text = (
                "Could not reach Gemini, so here are the most relevant passages instead:\n\n"
            )
            for i, ch in enumerate(retrieved, start=1):
                answer_text += f"[{i}] {ch.content}\n\n"

        return answer_text, retrieved

    # ---------- CV vs JD analysis ---------- #

    def analyze_cv_vs_jd(self, cv_path: str, jd_path: str) -> str:
        """
        Compare a single CV against a Job Description using Gemini.
        Returns a human-readable analysis in English.
        """
        cv_text = self._load_file_text(cv_path)
        jd_text = self._load_file_text(jd_path)

        if not cv_text.strip() or not jd_text.strip():
            return (
                "Could not read the CV or the Job Description. "
                "Please make sure you uploaded valid PDF or TXT files."
            )

        if self.model is None:
            return (
                "LLM is not configured, so CV vs JD analysis cannot be performed. "
                "Please set GEMINI_API_KEY first."
            )

        prompt = textwrap.dedent(
            f"""
            You are an expert career coach and technical recruiter.

            You are given a candidate's CV and a Job Description.

            CV:
            {cv_text}

            Job Description:
            {jd_text}

            Task:
            1) Evaluate how well the CV matches the Job Description (use one label: Low / Medium / High).
            2) List the top 3 strengths of the candidate for this role.
            3) List the top 3 missing or weak skills in the CV compared to the Job Description.
            4) Provide concrete, practical suggestions to improve the CV to better fit this role.

            Guidelines:
            - Answer in clear English.
            - Use headings and numbered or bulleted lists where appropriate.
            - Be specific and actionable, not generic.
            """
        )

        try:
            resp = self.model.generate_content(prompt)
            return resp.text.strip() if resp and resp.text else (
                "Gemini did not return any content for CV vs JD analysis."
            )
        except Exception:
            return "Could not reach Gemini while analyzing CV vs JD."
