from retrieval.semantic_retrieval import retrieve_evidence


questions = [
    "What is DMart?",
    "Where can I find basmati rice?",
    "What is the return policy?",
    "What are the store timings?",
    "Where can I find Dove shampoo?",
]


for question in questions:

    print("\n")
    print("=" * 80)
    print("QUESTION:", question)
    print("=" * 80)

    evidence = retrieve_evidence(question)

    print("\n--- PRIVATE EVIDENCE ---\n")

    if not evidence["private"]:
        print("No private evidence selected.")
    else:
        for result in evidence["private"]:
            print(
                "Source:",
                result["source"],
                "| Score:",
                round(result["score"], 4)
            )

    print("\n--- WEB EVIDENCE ---\n")

    if not evidence["web"]:
        print("No web evidence selected.")
    else:
        for result in evidence["web"]:
            print(
                "Title:",
                result["title"],
                "| Score:",
                round(result["score"], 4)
            )
            print("URL:", result["url"])