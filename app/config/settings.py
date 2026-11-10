import logging
import os
from functools import lru_cache

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(dotenv_path=os.path.join(_PROJECT_ROOT, ".env"))

DEFAULT_APP_NAME = "retail-ai-helper"


class Config:
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", DEFAULT_APP_NAME)
    SERVICE_VERSION: str = os.getenv("SERVICE_VERSION", "2.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @staticmethod
    def _parse_origins(raw: str) -> list[str]:
        return [o.strip() for o in raw.split(",") if o.strip()]

    CORS_ORIGINS: list[str] = _parse_origins(
        os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
        )
    )

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_CHAT_MODEL: str = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.0-flash")
    GEMINI_EMBED_MODEL: str = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")

    PRIVATE_MIN_SCORE: float = float(os.getenv("PRIVATE_MIN_SCORE", "0.55"))
    WEB_MIN_SCORE: float = float(os.getenv("WEB_MIN_SCORE", "0.55"))
    TOP_K: int = int(os.getenv("TOP_K", "3"))

    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    WEB_SEARCH_MAX_RESULTS: int = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "5"))

    MAX_HISTORY_PER_SESSION: int = int(os.getenv("MAX_HISTORY_PER_SESSION", "20"))

    # Set to "true" to classify intent with Gemini instead of keyword rules.
    USE_LLM_ROUTER: bool = os.getenv("USE_LLM_ROUTER", "false").lower() == "true"

    @classmethod
    def is_configured(cls) -> bool:
        if not cls.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not set; chat endpoints will fail")
            return False
        return True


@lru_cache(maxsize=1)
def get_settings() -> type[Config]:
    return Config
