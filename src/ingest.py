from pathlib import Path
import json
import re

RAW_DIR = Path("documents")
OUT_PATH = Path("data/processed/documents.json")


def clean_text(text: str) -> str:
    """Basic cleaning for copied text files."""
    # Remove obvious HTML tags if any copied source contains them.
    text = re.sub(r"<[^>]+>", " ", text)
    # Normalize whitespace while preserving paragraph boundaries.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_documents() -> list[dict]:
    documents = []
    for path in sorted(RAW_DIR.glob("*.txt")):
        raw_text = path.read_text(encoding="utf-8")
        cleaned = clean_text(raw_text)
        if not cleaned:
            continue
        documents.append({
            "source": path.name,
            "path": str(path),
            "text": cleaned,
        })
    return documents


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    documents = load_documents()
    OUT_PATH.write_text(json.dumps(documents, indent=2), encoding="utf-8")
    print(f"Saved {len(documents)} cleaned documents to {OUT_PATH}")
    if documents:
        print("\nPreview of first document:\n")
        print(documents[0]["text"][:1000])


if __name__ == "__main__":
    main()
