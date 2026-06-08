from pathlib import Path
import json
import re

IN_PATH = Path("data/processed/documents.json")
OUT_PATH = Path("data/chunks/chunks.json")

MIN_CHARS = 250
MAX_CHARS = 900
OVERLAP_CHARS = 100


def split_into_paragraphs(text: str) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return paragraphs


def chunk_document(text: str) -> list[str]:
    """
    Paragraph-aware chunking.
    This keeps review blocks together when possible instead of splitting every N characters.
    """
    paragraphs = split_into_paragraphs(text)
    chunks = []
    current = ""

    for para in paragraphs:
        # If a single paragraph is very long, split it with overlap.
        if len(para) > MAX_CHARS:
            if current:
                chunks.append(current.strip())
                current = ""
            start = 0
            while start < len(para):
                part = para[start:start + MAX_CHARS]
                chunks.append(part.strip())
                start += MAX_CHARS - OVERLAP_CHARS
            continue

        candidate = f"{current}\n\n{para}".strip() if current else para
        if len(candidate) <= MAX_CHARS:
            current = candidate
        else:
            if len(current) >= MIN_CHARS:
                chunks.append(current.strip())
                # Keep a little overlap from previous chunk for context.
                overlap = current[-OVERLAP_CHARS:] if len(current) > OVERLAP_CHARS else current
                current = f"{overlap}\n\n{para}".strip()
            else:
                chunks.append(candidate.strip())
                current = ""

    if current.strip():
        chunks.append(current.strip())

    return [c for c in chunks if len(c.strip()) > 0]


def main() -> None:
    documents = json.loads(IN_PATH.read_text(encoding="utf-8"))
    all_chunks = []

    for doc in documents:
        chunks = chunk_document(doc["text"])
        for i, chunk_text in enumerate(chunks):
            all_chunks.append({
                "id": f"{Path(doc['source']).stem}_{i}",
                "source": doc["source"],
                "chunk_index": i,
                "text": chunk_text,
            })

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(all_chunks, indent=2), encoding="utf-8")
    print(f"Saved {len(all_chunks)} chunks to {OUT_PATH}")
    print("\nFive sample chunks:\n")
    for sample in all_chunks[:5]:
        print("=" * 80)
        print(f"ID: {sample['id']}")
        print(f"Source: {sample['source']}")
        print(sample["text"][:1000])


if __name__ == "__main__":
    main()
