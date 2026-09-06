"""
Person 1 - Knowledge Base + RAG
TechNova Pvt. Ltd. Office Assistant

This file:
1. Reads policy PDFs from data/documents/
2. Extracts text and keeps the PDF filename as metadata
3. Splits documents into overlapping chunks
4. Creates local sentence-transformer embeddings
5. Stores vectors in a FAISS index
6. Retrieves the most relevant policy chunks
7. Optionally sends retrieved context to an LLM for a grounded answer
8. Returns the source PDF names for citation

Run:
    pip install -r requirements.txt
    python p1_rag.py

For a retrieval-only test, the program works without an API key.
For LLM answers, create .env with:
    GEMINI_API_KEY=your_key_here
"""

import os

# Use the Ubuntu system CA bundle for HTTPS connections.
# This keeps SSL verification enabled.
SYSTEM_CA = "/etc/ssl/certs/ca-certificates.crt"
os.environ["REQUESTS_CA_BUNDLE"] = SYSTEM_CA
os.environ["SSL_CERT_FILE"] = SYSTEM_CA
os.environ["CURL_CA_BUNDLE"] = SYSTEM_CA

from pathlib import Path
from typing import List, Dict, Tuple
import re

import numpy as np
import faiss
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from google import genai


BASE_DIR = Path(__file__).resolve().parent
DOCUMENT_DIR = BASE_DIR / "data" / "documents"

# A small, good general-purpose local embedding model.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# RAG settings. Keep these simple for the capstone.
CHUNK_SIZE = 700
CHUNK_OVERLAP = 120
TOP_K = 4


class PolicyRAG:
    """Build and query a vector index over company policy PDFs."""

    def __init__(
        self,
        document_dir: Path = DOCUMENT_DIR,
        model_name: str = EMBEDDING_MODEL,
    ):
        self.document_dir = Path(document_dir)
        self.model = SentenceTransformer(model_name)
        self.chunks: List[Dict] = []
        self.index = None

    # ---------- 1. LOAD PDFS ----------

    def load_pdfs(self) -> List[Dict]:
        """Extract text from every PDF and attach its source filename."""
        documents = []

        pdf_files = sorted(self.document_dir.glob("*.pdf"))

        if not pdf_files:
            raise FileNotFoundError(
                f"No PDF files found in: {self.document_dir}"
            )

        for pdf_path in pdf_files:
            reader = PdfReader(str(pdf_path))
            pages = []

            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                text = self.clean_text(text)

                if text:
                    pages.append(
                        {
                            "text": text,
                            "source": pdf_path.name,
                            "page": page_number,
                        }
                    )

            documents.extend(pages)

        return documents

    @staticmethod
    def clean_text(text: str) -> str:
        """Remove unnecessary whitespace while preserving readable text."""
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ---------- 2. CHUNKING ----------

    def create_chunks(self, documents: List[Dict]) -> List[Dict]:
        """
        Split each page into overlapping chunks.

        Metadata is retained so the final answer can cite the exact PDF/page.
        """
        chunks = []

        for doc in documents:
            text = doc["text"]
            start = 0

            while start < len(text):
                end = min(start + CHUNK_SIZE, len(text))
                chunk_text = text[start:end].strip()

                if chunk_text:
                    chunks.append(
                        {
                            "text": chunk_text,
                            "source": doc["source"],
                            "page": doc["page"],
                        }
                    )

                if end >= len(text):
                    break

                start = end - CHUNK_OVERLAP

        self.chunks = chunks
        return chunks

    # ---------- 3. EMBEDDINGS + VECTOR DB ----------

    def build_index(self) -> None:
        """Create embeddings and a FAISS cosine-similarity index."""
        if not self.chunks:
            raise ValueError("No chunks available. Run create_chunks() first.")

        texts = [item["text"] for item in self.chunks]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        ).astype("float32")

        dimension = embeddings.shape[1]

        # Inner product on normalized vectors = cosine similarity.
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

    # ---------- 4. RETRIEVAL ----------

    def search(self, query: str, top_k: int = TOP_K) -> List[Dict]:
        """Retrieve the most relevant policy chunks for a user query."""
        if self.index is None:
            raise ValueError("Index is not built. Call build_index() first.")

        if not query.strip():
            return []

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype("float32")

        scores, indices = self.index.search(
            query_embedding,
            min(top_k, len(self.chunks)),
        )

        results = []

        for score, index_position in zip(scores[0], indices[0]):
            if index_position == -1:
                continue

            item = dict(self.chunks[index_position])
            item["score"] = float(score)
            results.append(item)

        return results

    # ---------- 5. CONTEXT + CITATIONS ----------

    @staticmethod
    def build_context(results: List[Dict]) -> str:
        """Convert retrieved chunks into grounded LLM context."""
        blocks = []

        for number, result in enumerate(results, start=1):
            blocks.append(
                f"[Source {number}]\n"
                f"File: {result['source']}\n"
                f"Page: {result['page']}\n"
                f"Content: {result['text']}"
            )

        return "\n\n".join(blocks)

    @staticmethod
    def build_citations(results: List[Dict]) -> List[str]:
        """Return unique PDF/page citations."""
        citations = []
        seen = set()

        for result in results:
            citation = f"{result['source']} (page {result['page']})"

            if citation not in seen:
                citations.append(citation)
                seen.add(citation)

        return citations

    # ---------- 6. GEMINI LLM ANSWER ----------

    def generate_answer(
        self,
        query: str,
        results: List[Dict],
    ) -> str:
        """Generate a short, grounded answer using Gemini."""
        if not results:
            return (
                "I could not find relevant information in the company policy "
                "documents."
            )

        # Send the retrieved policy text to Gemini.
        context = self.build_context(results)

        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            return (
                "GEMINI_API_KEY is missing. Add it to the .env file "
                "to generate the final answer."
            )

        client = genai.Client(api_key=api_key)

        prompt = f"""
You are the policy assistant for TechNova Pvt. Ltd.

Answer the employee's question using ONLY the retrieved policy context.

STRICT RULES:
1. Give ONLY the direct answer.
2. Keep the answer to 2 or 3 short lines maximum.
3. Do NOT reproduce the PDF or the retrieved chunk.
4. Do NOT mention unrelated policies.
5. Do NOT invent or assume any policy rule.
6. If the answer is not present in the context, say: "The available policy documents do not provide this information."
7. Do NOT add a source/citation; the Python program will add the citation separately.

Employee question:
{query}

Retrieved policy context:
{context}
"""

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        answer = (response.text or "").strip()

        if not answer:
            return "The available policy documents do not provide this information."

        return answer

    # ---------- 7. ONE PUBLIC FUNCTION FOR OTHER TEAM MEMBERS ----------

    def search_company_policy(
        self,
        query: str,
        top_k: int = TOP_K,
        generate_llm_answer: bool = False,
    ) -> Dict:
        """
        Main function that Person 2 / the final application can call.

        Returns:
            {
                "answer": "...",
                "sources": [...],
                "results": [...]
            }
        """
        results = self.search(query, top_k=top_k)
        sources = self.build_citations(results)

        if generate_llm_answer:
            answer = self.generate_answer(query, results)
        else:
            answer = (
                "Relevant policy information retrieved successfully.\n\n"
                + "\n\n".join(
                    f"- {item['text']}" for item in results
                )
            )

        return {
            "answer": answer,
            "sources": sources,
            "results": results,
        }


def build_rag() -> PolicyRAG:
    """Reusable setup function for app.py / router.py."""
    rag = PolicyRAG()
    documents = rag.load_pdfs()
    rag.create_chunks(documents)
    rag.build_index()
    return rag


def print_retrieval_results(results: List[Dict]) -> None:
    """Pretty-print retrieval results for testing."""
    print("\n" + "=" * 70)
    print("TOP RETRIEVED POLICY CHUNKS")
    print("=" * 70)

    for i, result in enumerate(results, start=1):
        print(f"\n{i}. Score: {result['score']:.4f}")
        print(f"   Source: {result['source']}")
        print(f"   Page: {result['page']}")
        print(f"   Text: {result['text']}")


def main() -> None:
    print("Building TechNova Policy RAG...")
    print(f"Reading PDFs from: {DOCUMENT_DIR}")

    rag = build_rag()

    print(f"Loaded {len(rag.chunks)} chunks from company policy PDFs.")
    print("\nType 'exit' to stop.")

    while True:
        query = input("\nEmployee question: ").strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        results = rag.search(query, top_k=TOP_K)

        # Generate the final concise answer using Gemini.
        print("\n" + "-" * 70)
        print("ANSWER")
        print("-" * 70)
        print(rag.generate_answer(query, results))

        # Show the PDF/page used by RAG.
        print("\n" + "-" * 70)
        print("SOURCE")
        print("-" * 70)

        citations = rag.build_citations(results)
        for citation in citations:
            print(f"- {citation}")


if __name__ == "__main__":
    main()
