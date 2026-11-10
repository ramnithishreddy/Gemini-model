import logging

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService, get_chat_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, service: ChatService = Depends(get_chat_service)) -> ChatResponse:
    return service.ask(request.message, request.session_id)


@router.post("/stream")
async def chat_stream(
    request: ChatRequest, service: ChatService = Depends(get_chat_service)
) -> StreamingResponse:
    """SSE stream. Frames: start → token(s) → sources → end → [DONE]"""
    return StreamingResponse(
        service.stream(request.message, request.session_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
