from ingestion.loader import load_documents
from ingestion.cleaner import clean_text
from ingestion.chunker import chunk_document


def ingest_documents():

    documents = load_documents("documents")

    all_chunks = []

    for document in documents:

        cleaned_text = clean_text(
            document["text"]
        )

        cleaned_document = {
            **document,
            "text": cleaned_text
        }

        chunks = chunk_document(
            cleaned_document,
            chunk_size=500,
            overlap=100
        )

        all_chunks.extend(chunks)

    return all_chunks


if __name__ == "__main__":

    chunks = ingest_documents()

    print("\n==============================")
    print("DOCUMENT INGESTION")
    print("==============================")

    print(f"\nTotal chunks: {len(chunks)}")

    for chunk in chunks:

        print("\n------------------------------")

        print("Chunk ID:", chunk["chunk_id"])

        print("Source:", chunk["source"])

        print("Metadata:")
        print(chunk["metadata"])

        print("Text:")
        print(chunk["text"])