from rag.rag_pipeline import ask


question = "Where can I find basmati rice?"

answer, sources = ask(question)


print("==============================")
print("RAG ANSWER")
print("==============================")

print("\nQuestion:")
print(question)

print("\nAnswer:")
print(answer)

print("\n==============================")
print("SOURCES USED")
print("==============================")

for source in sources:

    print(
        f"\n{source['source']} "
        f"(similarity: {source['score']:.4f})"
    )