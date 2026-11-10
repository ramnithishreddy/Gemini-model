import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.correlation import get_or_generate_correlation_id, set_correlation_id

logger = logging.getLogger(__name__)

_CORRELATION_HEADERS = ("x-correlation-id", "x-request-id", "x-trace-id")
_SKIP_PATHS = {"/health", "/health/ready", "/health/startup"}


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Reads or generates a correlation ID per request and echoes it on the response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        correlation_id = next(
            (request.headers.get(h) for h in _CORRELATION_HEADERS if request.headers.get(h)),
            None,
        )
        if not correlation_id:
            correlation_id = get_or_generate_correlation_id()

        set_correlation_id(correlation_id)
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
