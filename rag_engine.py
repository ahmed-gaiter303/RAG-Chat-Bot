import os
import textwrap
from typing import List, Tuple

import faiss
import numpy as np
import google.generativeai as genai


class RetrievedChunk:
    def __init__(self, content: str, source: str):
        self.content = content
        self.source = source


class RAGEngine:
    def __init__(self, embedding_dim: int = 768):
        """
        تهيئة محرك الـ RAG:
        - تحميل/تهيئة موديل Gemini (لو فيه مفتاح).
        - تحضير FAISS index.
        """
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
        else:
            self.model = None

        self.embedding_dim = embedding_dim
        self.index = None
        self.chunks: List[RetrievedChunk] = []

    # ---------- Embeddings بسيطة (للديمو) ---------- #

    def _embed_text(self, texts: List[str]) -> np.ndarray:
        """
        دالة بسيطة لإنتاج embeddings بطول ثابت (embedding_dim).
        لمشروع production استبدلها بموديل حقيقي من sentence_transformers أو غيره.
        """
        vectors = []
        for t in texts:
            arr = np.zeros(self.embedding_dim, dtype="float32")
            for i, ch in enumerate(t.encode("utf-8")[: self.embedding_dim]):
                arr[i] = float(ch) / 255.0
            vectors.append(arr)
        return np.vstack(vectors)

    # ---------- بناء الـ index ---------- #

    def build_index(self, file_paths: List[str]) -> Tuple[int, int]:
        """
        يقسّم الملفات النصية إلى مقاطع ويُنشئ عليها FAISS index.
        يرجع (عدد الملفات, عدد المقاطع).
        """
        all_chunks: List[RetrievedChunk] = []

        for path in file_paths:
            if not os.path.exists(path):
                continue

            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            words = text.split()
            chunk_size = 400
            for i in range(0, len(words), chunk_size):
                chunk_words = words[i : i + chunk_size]
                content = " ".join(chunk_words).strip()
                if content:
                    all_chunks.append(
                        RetrievedChunk(content=content, source=os.path.basename(path))
                    )

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

    def _retrieve(self, query: str, top_k: int = 4) -> List[RetrievedChunk]:
        """
        يرجع أفضل top_k مقاطع من الـ index بناءً على تشابه embeddings.
        """
        if self.index is None or not self.chunks:
            return []

        q_emb = self._embed_text([query])
        distances, indices = self.index.search(q_emb, top_k)

        retrieved: List[RetrievedChunk] = []
        for idx in indices[0]:
            if 0 <= idx < len(self.chunks):
                retrieved.append(self.chunks[idx])

        return retrieved

    # ---------- توليد الإجابة بـ Gemini ---------- #

    def answer(self, query: str) -> Tuple[str, List[RetrievedChunk]]:
        """
        الواجهة التي يستدعيها streamlit_app:
        ترجع (النص النهائي, قائمة المقاطع المستخدمة).
        """
        retrieved = self._retrieve(query)

        if not retrieved:
            return "لم أجد أي مقاطع مرتبطة بسؤالك في المستندات.", []

        # لو مفيش موديل Gemini configured → رجّع snippets فقط
        if self.model is None:
            text = "هنا أهم المقاطع من مستنداتك المتعلقة بسؤالك:\n\n"
            for i, ch in enumerate(retrieved, start=1):
                text += f"[{i}] {ch.content}\n\n"
            return text, retrieved

        # بناء سياق المقاطع
        context_blocks = []
        for i, ch in enumerate(retrieved, start=1):
            context_blocks.append(f"[{i}] {ch.content}")
        context_text = "\n\n".join(context_blocks)

        prompt = textwrap.dedent(
            f"""
            أنت مساعد ذكاء اصطناعي للإجابة عن أسئلة المستخدم اعتمادًا فقط على المقاطع التالية من المستندات.

            سؤال المستخدم:
            {query}

            المقاطع المسترجعة من المستندات:
            {context_text}

            تعليمات عامة:
            - استخدم المعلومات الواضحة في المقاطع فقط، وتجنّب الاختراع أو التخمين من خارجها.
            - لو المعلومة غير مكتوبة صراحة ولكن يمكن استنتاجها منطقيًا من التواريخ أو العناوين، يجوز الاستنتاج بشكل معقول.
            - لو لا يمكن الإجابة إطلاقًا من المقاطع، قل للمستخدم بوضوح أن المعلومات غير متوفرة في المستندات.

            قواعد خاصة للسير الذاتية (CV):
            - لو السؤال عن "current role" أو "current job" أو "الدور الحالي" أو "الوظيفة الحالية":
              * ابحث في المقاطع عن الخبرة العملية (Professional Experience / Experience).
              * اختر أحدث وظيفة من حيث التاريخ أو آخر وظيفة مذكورة، واعتبرها "أحدث دور مهني".
              * أرجِع المسمى الوظيفي + اسم الشركة + نوع العمل إن وُجد (Remote / On‑Site).

            إخراج الإجابة:
            - أجب باللغة العربية ما لم يطلب المستخدم الإنجليزية صراحة.
            - اجعل الإجابة قصيرة وواضحة، ويمكنك استخدام نقاط مرقّمة لو هناك أكثر من نقطة مهمة.
            - لا تذكر أرقام المقاطع في النص، فهي للاستخدام الداخلي فقط.
            """
        )

        try:
            resp = self.model.generate_content(prompt)
            answer_text = resp.text.strip() if resp and resp.text else "تعذر توليد إجابة من Gemini."
        except Exception:
            # fallback لو حصل خطأ في Gemini (rate limit مثلًا)
            answer_text = "تعذر الاتصال بـ Gemini، لذا أعرض لك المقاطع الأكثر صلة:\n\n"
            for i, ch in enumerate(retrieved, start=1):
                answer_text += f"[{i}] {ch.content}\n\n"

        return answer_text, retrieved
