import threading
import time
import uuid
from collections import deque
from typing import Deque, Dict, Optional

from app.config import Config
from app.models.chat import HistoryEntry, Source


class SessionStore:
    """Thread-safe in-memory chat history. Swap for Redis/Postgres in production."""

    def __init__(self, max_history: int = Config.MAX_HISTORY_PER_SESSION) -> None:
        self._max_history = max_history
        self._sessions: Dict[str, Deque[HistoryEntry]] = {}
        self._lock = threading.Lock()

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        with self._lock:
            self._sessions[session_id] = deque(maxlen=self._max_history)
        return session_id

    def ensure_session(self, session_id: Optional[str]) -> str:
        if session_id:
            with self._lock:
                if session_id not in self._sessions:
                    self._sessions[session_id] = deque(maxlen=self._max_history)
            return session_id
        return self.create_session()

    def append(
        self,
        session_id: str,
        role: str,
        content: str,
        *,
        sources: Optional[list[Source]] = None,
        route: Optional[str] = None,
    ) -> None:
        entry = HistoryEntry(
            role=role,
            content=content,
            sources=sources or [],
            route=route,
            timestamp=time.time(),
        )
        with self._lock:
            self._sessions.setdefault(session_id, deque(maxlen=self._max_history)).append(entry)

    def get(self, session_id: str) -> list[HistoryEntry]:
        with self._lock:
            return list(self._sessions.get(session_id, []))

    def delete(self, session_id: str) -> bool:
        with self._lock:
            return self._sessions.pop(session_id, None) is not None


_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    global _store
    if _store is None:
        _store = SessionStore()
    return _store
