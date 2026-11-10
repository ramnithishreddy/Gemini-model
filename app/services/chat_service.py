import logging
import time
from typing import AsyncIterator, Optional

from app.config import Config
from app.models.chat import ChatResponse, Source
from app.services.llm_router import route_question
from app.services.session_service import SessionStore

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, session_store: SessionStore) -> None:
        self._sessions = session_store

    def _retrieve_and_answer(self, question: str) -> tuple[str, str, list[Source]]:
        from retrieval.semantic_retrieval import retrieve_evidence
        from retrieval.answer_generator import generate_answer

        route = route_question(question)
        evidence = retrieve_evidence(question)
        result = generate_answer(question, evidence)

        sources: list[Source] = [
            Source(type="private", source=s) for s in result.get("used_private_sources", [])
        ] + [
            Source(type="web", title=s.get("title", ""), url=s.get("url", ""))
            for s in result.get("used_web_sources", [])
        ]
        return result.get("answer", ""), route, sources

    def ask(self, question: str, session_id: Optional[str] = None) -> ChatResponse:
        session_id = self._sessions.ensure_session(session_id)
        start = time.perf_counter()

        if not question.strip():
            return ChatResponse(
                answer="Please enter a question.",
                route="error",
                sources=[],
                session_id=session_id,
                response_time_ms=0.0,
            )

        try:
            answer, route, sources = self._retrieve_and_answer(question)
        except Exception as exc:
            logger.exception("Chat pipeline failed: %s", exc)
            return ChatResponse(
                answer="Sorry — something went wrong.",
                route="error",
                sources=[],
                session_id=session_id,
                response_time_ms=(time.perf_counter() - start) * 1000,
            )

        self._sessions.append(session_id, "user", question)
        self._sessions.append(session_id, "assistant", answer, sources=sources, route=route)

        return ChatResponse(
            answer=answer,
            route=route,
            sources=sources,
            session_id=session_id,
            response_time_ms=(time.perf_counter() - start) * 1000,
        )

    async def stream(self, question: str, session_id: Optional[str] = None) -> AsyncIterator[str]:
        import json

        session_id = self._sessions.ensure_session(session_id)
        start = time.perf_counter()

        yield f"data: {json.dumps({'session_id': session_id, 'type': 'start'})}\n\n"

        try:
            answer, route, sources = self._retrieve_and_answer(question)
        except Exception as exc:
            logger.exception("Chat stream failed: %s", exc)
            yield f"data: {json.dumps({'type': 'error', 'message': 'Sorry — something went wrong.'})}\n\n"
            yield "data: [DONE]\n\n"
            return

        for chunk in _chunk_text(answer):
            yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

        yield f"data: {json.dumps({'type': 'sources', 'route': route, 'sources': [s.model_dump() for s in sources]})}\n\n"

        self._sessions.append(session_id, "user", question)
        self._sessions.append(session_id, "assistant", answer, sources=sources, route=route)

        elapsed = (time.perf_counter() - start) * 1000
        yield f"data: {json.dumps({'type': 'end', 'response_time_ms': elapsed})}\n\n"
        yield "data: [DONE]\n\n"


def _chunk_text(text: str, max_chars: int = 60) -> list[str]:
    if not text:
        return []
    words, chunks, buf, length = text.split(), [], [], 0
    for word in words:
        if length + len(word) + 1 > max_chars and buf:
            chunks.append(" ".join(buf) + " ")
            buf, length = [], 0
        buf.append(word)
        length += len(word) + 1
    if buf:
        chunks.append(" ".join(buf))
    return chunks


_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    global _chat_service
    if _chat_service is None:
        from app.services.session_service import get_session_store
        _chat_service = ChatService(get_session_store())
    return _chat_service
