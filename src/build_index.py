from pathlib import Path
import json
import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_PATH = Path("data/chunks/chunks.json")
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "unofficial_guide_chunks"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def main() -> None:
    chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    if not chunks:
        raise ValueError("No chunks found. Run src/ingest.py and src/chunk.py first.")

    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Delete old collection to avoid duplicate IDs while developing.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    collection.add(
        ids=[chunk["id"] for chunk in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"],
            }
            for chunk in chunks
        ],
    )

    print(f"Stored {len(chunks)} chunks in ChromaDB collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    main()
