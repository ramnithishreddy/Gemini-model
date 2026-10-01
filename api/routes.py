from fastapi import APIRouter
from pydantic import BaseModel

from retrieval.semantic_retrieval import retrieve_evidence
from retrieval.answer_generator import generate_answer


router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(request: ChatRequest):

    question = request.message.strip()

    if not question:
        return {
            "answer": "Please enter a question.",
            "sources": []
        }

    evidence = retrieve_evidence(question)

    result = generate_answer(
        question,
        evidence
    )

    sources = []

    for source in result.get("used_private_sources", []):
        sources.append({
            "type": "private",
            "source": source
        })

    for source in result.get("used_web_sources", []):
        sources.append({
            "type": "web",
            "title": source.get("title", ""),
            "url": source.get("url", "")
        })

    return {
        "answer": result.get("answer", ""),
        "sources": sources
    }