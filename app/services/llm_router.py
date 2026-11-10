"""Routes a question to 'private', 'web', or 'business' using either Gemini or keyword rules."""

import logging
from typing import Literal

from app.config import Config

try:
    from router.router import route_question as _keyword_route
except ImportError:
    def _keyword_route(question: str) -> str:
        return "private"

logger = logging.getLogger(__name__)

Route = Literal["private", "web", "business"]

_PROMPT = (
    "Classify this retail store question into exactly one label: "
    "private (store policies/layout/products), web (company news/external info), "
    "business (stock/prices/orders). Reply with one lowercase word only.\n\nQuestion: {question}\nLabel:"
)


def _llm_route(question: str) -> Route:
    try:
        from google import genai
        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        result = client.models.generate_content(
            model=Config.GEMINI_CHAT_MODEL,
            contents=_PROMPT.format(question=question),
        )
        label = (result.text or "").strip().lower()
        if label in ("private", "web", "business"):
            return label  # type: ignore[return-value]
    except Exception as exc:
        logger.warning("LLM router failed (%s); falling back to keywords", exc)
    return _keyword_route(question)  # type: ignore[return-value]


def route_question(question: str) -> Route:
    if Config.USE_LLM_ROUTER and Config.GEMINI_API_KEY:
        return _llm_route(question)
    return _keyword_route(question)  # type: ignore[return-value]
