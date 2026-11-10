import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import chat_router, health_router, history_router
from app.config import Config
from app.middleware import CorrelationMiddleware
from app.utils.logging_setup import setup_logging

setup_logging(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting %s v%s (env=%s)", Config.SERVICE_NAME, Config.SERVICE_VERSION, Config.ENVIRONMENT)
    Config.is_configured()
    yield
    logger.info("Shutting down %s", Config.SERVICE_NAME)


app = FastAPI(
    title="Retail AI Helper",
    description="Gemini-powered RAG assistant for a retail store.",
    version=Config.SERVICE_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID"],
)
app.add_middleware(CorrelationMiddleware)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(health_router)
app.include_router(chat_router)
app.include_router(history_router)


@app.get("/")
def root() -> dict:
    return {
        "service": Config.SERVICE_NAME,
        "version": Config.SERVICE_VERSION,
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "chat_stream": "/chat/stream",
            "history": "/history/{session_id}",
            "docs": "/docs",
        },
    }
