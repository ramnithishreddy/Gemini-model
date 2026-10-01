from ingestion.ingest import ingest_documents
from ingestion.embedder import create_embedding
from rag.vector_store import save_vectors


def build_vector_store():

    print("==============================")
    print("BUILDING VECTOR STORE")
    print("==============================")

    chunks = ingest_documents()

    print(f"\nTotal chunks: {len(chunks)}")

    for chunk in chunks:
        print(f"\nEmbedding: {chunk['chunk_id']}")

        chunk["embedding"] = create_embedding(
            chunk["text"]
        )

    save_vectors(chunks)

    print("\nVector store created successfully.")


if __name__ == "__main__":
    build_vector_store()