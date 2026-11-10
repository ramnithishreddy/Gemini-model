from typing import Literal, Optional

from pydantic import BaseModel, Field


class Source(BaseModel):
    type: Literal["private", "web", "business"]
    source: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    score: Optional[float] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None
    stream: bool = False


class ChatResponse(BaseModel):
    answer: str
    route: Literal["private", "web", "business", "error"]
    sources: list[Source] = Field(default_factory=list)
    session_id: str
    response_time_ms: float


class HistoryEntry(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    sources: list[Source] = Field(default_factory=list)
    route: Optional[str] = None
    timestamp: float


class HistoryResponse(BaseModel):
    session_id: str
    turns: list[HistoryEntry]
