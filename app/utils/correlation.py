import uuid
from contextvars import ContextVar
from typing import Optional

_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


def generate_correlation_id() -> str:
    return str(uuid.uuid4())


def get_correlation_id() -> Optional[str]:
    return _correlation_id.get()


def set_correlation_id(value: str) -> None:
    _correlation_id.set(value)


def get_or_generate_correlation_id() -> str:
    existing = _correlation_id.get()
    if existing:
        return existing
    new = generate_correlation_id()
    _correlation_id.set(new)
    return new
