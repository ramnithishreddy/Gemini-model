import json
from pathlib import Path


STORE_PATH = Path("vector_store/store.json")


def save_vectors(chunks):
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)

    data = []

    for chunk in chunks:
        data.append({
            "chunk_id": chunk["chunk_id"],
            "source": chunk["source"],
            "chunk_index": chunk["chunk_index"],
            "text": chunk["text"],
            "metadata": chunk["metadata"],
            "embedding": chunk["embedding"]
        })

    with open(STORE_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file)

    print(f"Saved {len(data)} vectors.")


def load_vectors():
    if not STORE_PATH.exists():
        raise FileNotFoundError(
            "Vector store not found. Run the ingestion pipeline first."
        )

    with open(STORE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)