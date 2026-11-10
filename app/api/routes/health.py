import time

from fastapi import APIRouter

from app.config import Config

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check() -> dict:
    return {"status": "healthy", "service": Config.SERVICE_NAME, "version": Config.SERVICE_VERSION, "timestamp": time.time()}


@router.get("/ready")
def readiness_check() -> dict:
    gemini_ready = bool(Config.GEMINI_API_KEY)
    return {
        "status": "ready" if gemini_ready else "not_ready",
        "checks": {"gemini_api_key": "set" if gemini_ready else "missing"},
        "service": Config.SERVICE_NAME,
        "timestamp": time.time(),
    }


@router.get("/startup")
def startup_check() -> dict:
    return {"status": "started", "service": Config.SERVICE_NAME, "version": Config.SERVICE_VERSION, "timestamp": time.time()}
