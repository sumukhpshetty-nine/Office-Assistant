"""
Person 1 - Knowledge Base + RAG
TechNova Pvt. Ltd. Office Assistant

This file:
1. Reads policy PDFs from data/documents/
2. Extracts text and keeps the PDF filename as metadata
3. Splits documents into sentence-aware overlapping chunks
4. Creates local sentence-transformer embeddings
5. Stores vectors in a FAISS index
6. Retrieves the most relevant policy chunks
7. Optionally sends retrieved context to Gemini
8. Returns source PDF names and page numbers

Run:
    pip install -r requirements.txt
    python person1/p1_rag.py

For retrieval-only testing:
    No API key is required.

For Gemini-generated answers, create a .env file:
    GEMINI_API_KEY=your_key_here
"""

import os
import re
from pathlib import Path
from typing import Dict, List


# -------------------------------------------------------------------
# SSL CONFIGURATION
# -------------------------------------------------------------------

# Use the Ubuntu system CA bundle for HTTPS connections.
# SSL verification remains enabled.
SYSTEM_CA = "/etc/ssl/certs/ca-certificates.crt"

os.environ["REQUESTS_CA_BUNDLE"] = SYSTEM_CA
os.environ["SSL_CERT_FILE"] = SYSTEM_CA
os.environ["CURL_CA_BUNDLE"] = SYSTEM_CA


# -------------------------------------------------------------------
# THIRD-PARTY IMPORTS
# -------------------------------------------------------------------

import faiss
import numpy as np
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# If this script is inside person1/, documents should be inside:
# person1/data/documents/
DOCUMENT_DIR = BASE_DIR / "data" / "documents"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

CHUNK_SIZE = 700
CHUNK_OVERLAP = 120
TOP_K = 4

GEMINI_MODEL = "gemini-3.6-flash"


# -------------------------------------------------------------------
# POLICY RAG CLASS
# -------------------------------------------------------------------

class PolicyRAG:
    """Build and query a vector index over company policy PDFs."""

    def __init__(
        self,
        document_dir: Path = DOCUMENT_DIR,
        model_name: str = EMBEDDING_MODEL,
    ):
        self.document_dir = Path(document_dir)

        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

        self.chunks: List[Dict] = []
        self.index = None

    # ----------------------------------------------------------------
    # 1. LOAD PDFS
    # ----------------------------------------------------------------

    def load_pdfs(self) -> List[Dict]:
        """
        Extract text from every PDF and attach source filename
        and page number as metadata.
        """
        documents = []

        pdf_files = sorted(self.document_dir.glob("*.pdf"))

        if not pdf_files:
            raise FileNotFoundError(
                f"No PDF files found in: {self.document_dir}"
            )

        print(f"Found {len(pdf_files)} PDF files.")

        for pdf_path in pdf_files:
            print(f"Reading: {pdf_path.name}")

            reader = PdfReader(str(pdf_path))

            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                text = self.clean_text(text)

                if text:
                    documents.append(
                        {
                            "text": text,
                            "source": pdf_path.name,
                            "page": page_number,
                        }
                    )

        print(f"Extracted text from {len(documents)} pages.")

        return documents

    # ----------------------------------------------------------------
    # 2. CLEAN TEXT
    # ----------------------------------------------------------------

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Remove unnecessary whitespace while preserving readable text.
        """
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ----------------------------------------------------------------
    # 3. SENTENCE-AWARE CHUNKING
    # ----------------------------------------------------------------

    def create_chunks(self, documents: List[Dict]) -> List[Dict]:
        """
        Split each page into sentence-aware overlapping chunks.

        This avoids cutting words and sentences in the middle.
        Metadata is retained for PDF/page citations.
        """
        chunks = []

        for doc in documents:
            text = self.clean_text(doc["text"])

            if not text:
                continue

            # Split on sentence-ending punctuation.
            # Punctuation is preserved.
            sentences = re.split(
                r"(?<=[.!?])\s+",
                text,
            )

            current_sentences = []
            current_length = 0

            for sentence in sentences:
                sentence = sentence.strip()

                if not sentence:
                    continue

                sentence_length = len(sentence)

                # Add sentence if it fits in the current chunk.
                # A long individual sentence is allowed as its own chunk.
                if (
                    current_length + sentence_length + 1 <= CHUNK_SIZE
                    or not current_sentences
                ):
                    current_sentences.append(sentence)
                    current_length += sentence_length + 1

                else:
                    # Save the current chunk.
                    chunk_text = " ".join(current_sentences).strip()

                    if chunk_text:
                        chunks.append(
                            {
                                "text": chunk_text,
                                "source": doc["source"],
                                "page": doc["page"],
                            }
                        )

                    # Keep recent sentences as overlap.
                    overlap_sentences = []
                    overlap_length = 0

                    for previous_sentence in reversed(
                        current_sentences
                    ):
                        previous_length = len(previous_sentence) + 1

                        if (
                            overlap_length + previous_length
                            > CHUNK_OVERLAP
                        ):
                            break

                        overlap_sentences.insert(
                            0,
                            previous_sentence,
                        )

                        overlap_length += previous_length

                    # Start the next chunk with overlap plus
                    # the current sentence.
                    current_sentences = (
                        overlap_sentences + [sentence]
                    )

                    current_length = sum(
                        len(item) + 1
                        for item in current_sentences
                    )

            # Save the final remaining chunk.
            if current_sentences:
                final_chunk = " ".join(
                    current_sentences
                ).strip()

                if final_chunk:
                    chunks.append(
                        {
                            "text": final_chunk,
                            "source": doc["source"],
                            "page": doc["page"],
                        }
                    )

        self.chunks = chunks

        print(f"Created {len(chunks)} chunks.")

        return chunks

    # ----------------------------------------------------------------
    # 4. EMBEDDINGS + FAISS VECTOR DATABASE
    # ----------------------------------------------------------------

    def build_index(self) -> None:
        """
        Create embeddings and a FAISS cosine-similarity index.
        """
        if not self.chunks:
            raise ValueError(
                "No chunks available. Run create_chunks() first."
            )

        texts = [
            item["text"]
            for item in self.chunks
        ]

        print("Creating embeddings...")

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        ).astype("float32")

        dimension = embeddings.shape[1]

        # Inner product on normalized vectors is cosine similarity.
        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        print(
            f"FAISS index created with {self.index.ntotal} vectors."
        )

    # ----------------------------------------------------------------
    # 5. RETRIEVAL
    # ----------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = TOP_K,
    ) -> List[Dict]:
        """
        Retrieve the most relevant policy chunks for a query.
        """
        if self.index is None:
            raise ValueError(
                "Index is not built. Call build_index() first."
            )

        if not query or not query.strip():
            return []

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype("float32")

        number_of_results = min(
            top_k,
            len(self.chunks),
        )

        scores, indices = self.index.search(
            query_embedding,
            number_of_results,
        )

        results = []

        for score, index_position in zip(
            scores[0],
            indices[0],
        ):
            if index_position == -1:
                continue

            item = dict(
                self.chunks[index_position]
            )

            item["score"] = float(score)

            results.append(item)

        return results

    # ----------------------------------------------------------------
    # 6. BUILD LLM CONTEXT
    # ----------------------------------------------------------------

    @staticmethod
    def build_context(
        results: List[Dict],
    ) -> str:
        """
        Convert retrieved chunks into grounded LLM context.
        """
        blocks = []

        for number, result in enumerate(
            results,
            start=1,
        ):
            blocks.append(
                f"[Source {number}]\n"
                f"File: {result['source']}\n"
                f"Page: {result['page']}\n"
                f"Content: {result['text']}"
            )

        return "\n\n".join(blocks)

    # ----------------------------------------------------------------
    # 7. BUILD CITATIONS
    # ----------------------------------------------------------------

    @staticmethod
    def build_citations(
        results: List[Dict],
    ) -> List[str]:
        """
        Return unique PDF/page citations.
        """
        citations = []
        seen = set()

        for result in results:
            citation = (
                f"{result['source']} "
                f"(page {result['page']})"
            )

            if citation not in seen:
                citations.append(citation)
                seen.add(citation)

        return citations

    # ----------------------------------------------------------------
    # 8. GEMINI ANSWER GENERATION
    # ----------------------------------------------------------------

    def generate_answer(
        self,
        query: str,
        results: List[Dict],
    ) -> str:
        """
        Generate a short, grounded answer using Gemini.
        """
        if not results:
            return (
                "I could not find relevant information in "
                "the company policy documents."
            )

        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            return (
                "GEMINI_API_KEY is missing. Add it to the "
                ".env file to generate the final answer."
            )

        context = self.build_context(results)

        client = genai.Client(
            api_key=api_key
        )

        prompt = f"""
You are the policy assistant for TechNova Pvt. Ltd.

Answer the employee's question using ONLY the retrieved
policy context.

STRICT RULES:
1. Give only the direct answer.
2. Keep the answer to 2 or 3 short lines maximum.
3. Do not reproduce the PDF or the retrieved chunks.
4. Do not mention unrelated policies.
5. Do not invent or assume any policy rule.
6. If the answer is not present in the context, say:
   "The available policy documents do not provide this information."
7. Do not add a source or citation.
   The Python program will add the citation separately.

Employee question:
{query}

Retrieved policy context:
{context}
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        answer = (
            response.text or ""
        ).strip()

        if not answer:
            return (
                "The available policy documents do not "
                "provide this information."
            )

        return answer

    # ----------------------------------------------------------------
    # 9. PUBLIC FUNCTION FOR OTHER TEAM MEMBERS
    # ----------------------------------------------------------------

    def search_company_policy(
        self,
        query: str,
        top_k: int = TOP_K,
        generate_llm_answer: bool = False,
    ) -> Dict:
        """
        Main function that router.py or app.py can call.

        Returns:
            {
                "answer": "...",
                "sources": [...],
                "results": [...]
            }
        """
        results = self.search(
            query,
            top_k=top_k,
        )

        sources = self.build_citations(
            results
        )

        if generate_llm_answer:
            answer = self.generate_answer(
                query,
                results,
            )

        else:
            if not results:
                answer = (
                    "I could not find relevant information "
                    "in the company policy documents."
                )

            else:
                answer = (
                    "Relevant policy information:\n\n"
                    + "\n\n".join(
                        f"- {item['text']}"
                        for item in results
                    )
                )

        return {
            "answer": answer,
            "sources": sources,
            "results": results,
        }


# -------------------------------------------------------------------
# 10. BUILD RAG
# -------------------------------------------------------------------

def build_rag() -> PolicyRAG:
    """
    Reusable setup function for app.py or router.py.
    """
    rag = PolicyRAG()

    documents = rag.load_pdfs()

    rag.create_chunks(
        documents
    )

    rag.build_index()

    return rag


# -------------------------------------------------------------------
# 11. PRINT RETRIEVAL RESULTS
# -------------------------------------------------------------------

def print_retrieval_results(
    results: List[Dict],
) -> None:
    """
    Pretty-print retrieved chunks for debugging.
    """
    print("\n" + "=" * 70)
    print("TOP RETRIEVED POLICY CHUNKS")
    print("=" * 70)

    for number, result in enumerate(
        results,
        start=1,
    ):
        print(f"\n{number}. Score: {result['score']:.4f}")
        print(f"   Source: {result['source']}")
        print(f"   Page: {result['page']}")
        print(f"   Text: {result['text']}")


# -------------------------------------------------------------------
# 12. COMMAND-LINE TEST
# -------------------------------------------------------------------

def main() -> None:
    print("Building TechNova Policy RAG...")
    print(f"Reading PDFs from: {DOCUMENT_DIR}")

    rag = build_rag()

    print(
        f"Loaded {len(rag.chunks)} chunks "
        "from company policy PDFs."
    )

    print("\nType 'exit' to stop.")

    while True:
        query = input(
            "\nEmployee question: "
        ).strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        results = rag.search(
            query,
            top_k=TOP_K,
        )

        print("\n" + "-" * 70)
        print("ANSWER")
        print("-" * 70)

        # Retrieval-only answer. This does not use Gemini.
        result = rag.search_company_policy(
            query,
            top_k=TOP_K,
            generate_llm_answer=False,
        )

        print(result["answer"])

        print("\n" + "-" * 70)
        print("SOURCE")
        print("-" * 70)

        citations = rag.build_citations(
            results
        )

        for citation in citations:
            print(f"- {citation}")


# -------------------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------------------

if __name__ == "__main__":
    main()