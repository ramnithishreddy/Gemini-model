from ingestion.ingest import ingest_documents
from ingestion.embedder import create_embedding


chunks = ingest_documents()

print("\n==============================")
print("EMBEDDING PIPELINE")
print("==============================")

for chunk in chunks:

    embedding = create_embedding(chunk["text"])

    print("\n------------------------------")

    print("Chunk:", chunk["chunk_id"])

    print("Source:", chunk["source"])

    print("Embedding dimensions:", len(embedding))

    print("First 5 values:", embedding[:5])