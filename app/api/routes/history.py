from fastapi import APIRouter, Depends, HTTPException

from app.models.chat import HistoryResponse
from app.services.session_service import SessionStore, get_session_store

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{session_id}", response_model=HistoryResponse)
def get_history(session_id: str, store: SessionStore = Depends(get_session_store)) -> HistoryResponse:
    turns = store.get(session_id)
    if not turns:
        raise HTTPException(status_code=404, detail=f"No history for session {session_id!r}")
    return HistoryResponse(session_id=session_id, turns=turns)


@router.delete("/{session_id}")
def delete_history(session_id: str, store: SessionStore = Depends(get_session_store)) -> dict:
    return {"session_id": session_id, "deleted": store.delete(session_id)}
