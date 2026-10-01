from retrieval.semantic_retrieval import retrieve_evidence
from retrieval.answer_generator import generate_answer


question = "Where can I find basmati rice?"

evidence = retrieve_evidence(question)

answer = generate_answer(
    question,
    evidence
)

print("\n==============================")
print("QUESTION")
print("==============================")
print(question)

print("\n==============================")
print("ANSWER")
print("==============================")
print(answer)

print("\n==============================")
print("SOURCES USED AS CANDIDATES")
print("==============================")

for result in evidence["private"]:
    print(
        "PRIVATE:",
        result["source"],
        round(result["score"], 4)
    )

for result in evidence["web"]:
    print(
        "WEB:",
        result["title"],
        round(result["score"], 4)
    )