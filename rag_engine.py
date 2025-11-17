import os
import textwrap
from typing import List, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader


class RetrievedChunk:
    def __init__(self, content: str, source: str):
        self.content = content
        self.source = source


class RAGEngine:
    def __init__(self, embedding_dim: int = 384):
        """
        محرك RAG:
        - يقرأ ملفات PDF و TXT.
        - يبني FAISS index على Embeddings من SentenceTransformer.
        """
        # موديل الـ embeddings
        self.embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.embedding_dim = embedding_dim

        # ممكن تضيف هنا Gemini لو حابب (أنت already ضايفه)
        from google.generativeai import GenerativeModel, configure

        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            configure(api_key=api_key)
            self.model = GenerativeModel("gemini-2.5-flash")
        else:
            self.model = None

        self.index = None
        self.chunks: List[RetrievedChunk] = []

    # ---------- قراءة الملفات ---------- #

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
            return ""  # أنواع أخرى نتجاهلها حاليًا

    # ---------- Embeddings ---------- #

    def _embed_text(self, texts: List[str]) -> np.ndarray:
        """
        يحوّل قائمة نصوص إلى مصفوفة Embeddings (n x d).
        """
        embs = self.embed_model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        embs = embs.astype("float32")
        return embs

    # ---------- بناء الـ index ---------- #

    def build_index(self, file_paths: List[str]) -> Tuple[int, int]:
        """
        يقرأ الملفات، يقسّمها إلى مقاطع، يبني عليها FAISS index.
        يرجع: (عدد الملفات, عدد المقاطع).
        """
        all_chunks: List[RetrievedChunk] = []

        for path in file_paths:
            if not os.path.exists(path):
                continue

            raw_text = self._load_file_text(path)
            if not raw_text.strip():
                continue

            # تقسيم إلى مقاطع ~ 500 حرف (تقريبًا 100–150 كلمة)
            chunk_size = 500
            overlap = 100
            text = raw_text.replace("\r", "\n")
            text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk = text[start:end].strip()
                if chunk:
                    all_chunks.append(
                        RetrievedChunk(content=chunk, source=os.path.basename(path))
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

    # ---------- استرجاع المقاطع ---------- #

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

    # ---------- توليد الإجابة ---------- #

    def answer(self, query: str) -> Tuple[str, List[RetrievedChunk]]:
        retrieved = self._retrieve(query)

        if not retrieved:
            return "لم أجد أي مقاطع مرتبطة بسؤالك في المستندات.", []

        # لو مفيش Gemini: رجّع المقاطع نفسها
        if self.model is None:
            text = "هنا أهم المقاطع من مستنداتك المتعلقة بسؤالك:\n\n"
            for i, ch in enumerate(retrieved, start=1):
                text += f"[{i}] {ch.content}\n\n"
            return text, retrieved

        context_blocks = []
        for i, ch in enumerate(retrieved, start=1):
            context_blocks.append(f"[{i}] {ch.content}")
        context_text = "\n\n".join(context_blocks)

        prompt = textwrap.dedent(
            f"""
            أنت مساعد ذكاء اصطناعي يجيب عن أسئلة المستخدم بالاعتماد على المقاطع التالية من المستندات.

            سؤال المستخدم:
            {query}

            المقاطع المسترجعة:
            {context_text}

            التعليمات:
            - استخدم المعلومات الواضحة في المقاطع بشكل أساسي، ويمكنك الاستنتاج المنطقي البسيط عند الحاجة.
            - لو السؤال عن سيرة ذاتية (CV)، يمكنك استخراج:
              * الملخص المهني.
              * الوظائف، المسمّى الوظيفي، الشركات، والتواريخ.
              * المهارات التقنية.
              * الشهادات.
            - لا تقل إن المعلومات غير موجودة إلا إذا لم تجد أي شيء متعلق بالسؤال في المقاطع.
            - أجب باللغة نفسها التي استخدمها المستخدم (عربي أو إنجليزي).
            - اجعل الإجابة قصيرة وواضحة، ويمكنك استخدام نقاط مرقّمة عند الحاجة.
            """
        )

        try:
            resp = self.model.generate_content(prompt)
            answer_text = resp.text.strip() if resp and resp.text else "تعذر توليد إجابة من Gemini."
        except Exception:
            answer_text = "تعذر الاتصال بـ Gemini، لذا أعرض لك المقاطع الأكثر صلة:\n\n"
            for i, ch in enumerate(retrieved, start=1):
                answer_text += f"[{i}] {ch.content}\n\n"

        return answer_text, retrieved
