import os
from typing import Any

import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

load_dotenv()

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "unofficial_guide_chunks"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5

_model = SentenceTransformer(EMBEDDING_MODEL)
_chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def retrieve(question: str, k: int = TOP_K) -> list[dict[str, Any]]:
    query_embedding = _model.encode([question]).tolist()[0]
    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []
    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved.append({
            "text": doc,
            "source": meta.get("source", "unknown"),
            "chunk_index": meta.get("chunk_index", "unknown"),
            "distance": distance,
        })
    return retrieved


def format_context(chunks: list[dict[str, Any]]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(
            f"[Chunk {i}]\n"
            f"Source: {chunk['source']}\n"
            f"Chunk Index: {chunk['chunk_index']}\n"
            f"Text: {chunk['text']}"
        )
    return "\n\n".join(parts)


def generate_answer(question: str, chunks: list[dict[str, Any]]) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "GROQ_API_KEY is missing. Add it to your .env file before running generation."

    client = Groq(api_key=api_key)
    model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    context = format_context(chunks)

    prompt = f"""
You are a grounded question-answering assistant for an unofficial student guide.

Use ONLY the context below. Do not use outside knowledge.
If the context does not contain enough information to answer the question, say exactly:
"I don't have enough information in the provided documents to answer that."

When you answer, cite the source file names you used.

Context:
{context}

Question: {question}
""".strip()

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You answer only from provided retrieval context and cite source file names."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content


def ask(question: str) -> dict[str, Any]:
    chunks = retrieve(question)
    answer = generate_answer(question, chunks)
    sources = sorted({chunk["source"] for chunk in chunks})
    retrieved_preview = [
        {
            "source": chunk["source"],
            "chunk_index": chunk["chunk_index"],
            "distance": round(float(chunk["distance"]), 4),
            "text": chunk["text"],
        }
        for chunk in chunks
    ]
    return {
        "answer": answer,
        "sources": sources,
        "retrieved_chunks": retrieved_preview,
    }


if __name__ == "__main__":
    while True:
        question = input("\nAsk a question or type 'quit': ").strip()
        if question.lower() in {"quit", "exit"}:
            break
        result = ask(question)
        print("\nANSWER:\n")
        print(result["answer"])
        print("\nRETRIEVED SOURCES:")
        for chunk in result["retrieved_chunks"]:
            print(f"- {chunk['source']} | chunk {chunk['chunk_index']} | distance {chunk['distance']}")
