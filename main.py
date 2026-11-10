# Legacy shim — existing `uvicorn main:app` commands still work.
from app.main import app

__all__ = ["app"]
