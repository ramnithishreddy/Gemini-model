from ingestion.ingest import ingest_documents
from ingestion.embedder import create_embedding
from rag.similarity import cosine_similarity


print("==============================")
print("SEMANTIC SEARCH")
print("==============================")


# --------------------------------
# 1. Load document chunks
# --------------------------------

chunks = ingest_documents()

print(f"\nLoaded {len(chunks)} chunks.")


# --------------------------------
# 2. Create embeddings
# --------------------------------

for chunk in chunks:

    print(f"\nEmbedding: {chunk['source']}")

    chunk["embedding"] = create_embedding(
        chunk["text"]
    )


# --------------------------------
# 3. Ask a question
# --------------------------------

question = "Where can I find basmati rice?"

print("\nQuestion:")
print(question)


# --------------------------------
# 4. Embed the question
# --------------------------------

question_embedding = create_embedding(
    question
)


# --------------------------------
# 5. Calculate similarity
# --------------------------------

results = []

for chunk in chunks:

    score = cosine_similarity(
        question_embedding,
        chunk["embedding"]
    )

    results.append({
    "source": chunk["source"],
    "text": chunk["text"],
    "score": score,
    "metadata": chunk["metadata"]
})


# --------------------------------
# 6. Sort by similarity
# --------------------------------

results.sort(
    key=lambda item: item["score"],
    reverse=True
)


# --------------------------------
# 7. Display results
# --------------------------------

print("\n==============================")
print("SEARCH RESULTS")
print("==============================")

for result in results:

    print("\n------------------------------")

    print("Source:", result["source"])

    print("Similarity:",
          round(result["score"], 4))

    print("Text:")
    print(result["text"])