# Retail AI Helper (Gemini)

A Gemini-powered retrieval-augmented chat API for a retail store, with a
semantic private-knowledge store, an approved-web RAG fallback, and
structured chat sessions.

## Architecture

Rebuilt around the service patterns used in CVS Health's internal Lumina
and Sara (cvshdp-dataportal-ai-svcs) services:

```
gemini-model/
├── app/                       # new HTTP + service layer
│   ├── main.py                # FastAPI entrypoint (lifespan, middleware, routers)
│   ├── config/                # centralised settings
│   │   └── settings.py
│   ├── middleware/            # correlation-ID middleware
│   │   └── correlation_middleware.py
│   ├── models/                # pydantic request / response models
│   │   └── chat.py
│   ├── services/              # orchestration
│   │   ├── chat_service.py        # routing → retrieval → generation
│   │   ├── llm_router.py          # keyword / LLM intent classification
│   │   └── session_service.py     # chat-history store
│   ├── api/
│   │   └── routes/
│   │       ├── chat.py            # POST /chat + POST /chat/stream (SSE)
│   │       ├── health.py          # /health, /health/ready, /health/startup
│   │       └── history.py         # GET/DELETE /history/{session_id}
│   └── utils/
│       ├── correlation.py         # ContextVar-based correlation ID
│       └── logging_setup.py       # structured logs with correlation IDs
│
├── ingestion/                 # document loading, chunking, embedding
├── rag/                       # vector store + similarity + retriever
├── retrieval/                 # semantic_retrieval + answer_generator
├── router/                    # legacy keyword router (kept)
├── web_search/                # Tavily-backed web RAG
├── chat/                      # standalone chatbot utility
└── main.py                    # legacy shim → re-exports app.main.app
```

### Why this layout

| Pattern (from Lumina / Sara)       | Where it lives here                                      |
|------------------------------------|----------------------------------------------------------|
| Correlation-ID per request         | `app/middleware/correlation_middleware.py`               |
| Structured logs                    | `app/utils/logging_setup.py`                             |
| Centralised Config class           | `app/config/settings.py`                                 |
| FastAPI `lifespan` on startup      | `app/main.py`                                            |
| `/health`, `/ready`, `/startup`    | `app/api/routes/health.py`                               |
| Request/response Pydantic models   | `app/models/chat.py`                                     |
| Service layer separate from routes | `app/services/`                                          |
| Server-Sent-Event streaming        | `POST /chat/stream` → `app/services/chat_service.stream` |
| LLM-based intent classifier        | `app/services/llm_router.py`                             |
| Per-session chat history           | `app/services/session_service.py`                        |

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env         # fill in GEMINI_API_KEY etc.
```

Build the vector store (one-off, after dropping documents into `documents/`):

```bash
python -m ingestion.build_vector_store
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
# docs:   http://localhost:8000/docs
# health: http://localhost:8000/health
```

## API

### `POST /chat`

```json
{
  "message": "Where can I find basmati rice?",
  "session_id": null,
  "stream": false
}
```

Response:

```json
{
  "answer": "Basmati rice is in the grocery section ...",
  "route": "private",
  "sources": [{"type": "private", "source": "store_layout.md"}],
  "session_id": "7a9...",
  "response_time_ms": 412.3
}
```

### `POST /chat/stream`

Same body. Response is `text/event-stream`:

```
data: {"type": "start", "session_id": "7a9..."}
data: {"type": "token", "content": "Basmati rice "}
data: {"type": "token", "content": "is in the grocery section ..."}
data: {"type": "sources", "route": "private", "sources": [...]}
data: {"type": "end", "response_time_ms": 412.3}
data: [DONE]
```

### `GET /history/{session_id}`

Returns every turn recorded for a session.

### `DELETE /history/{session_id}`

Drops that session's history.

## Configuration

See `.env.example`. Key knobs:

| Variable           | Default                | Notes                                          |
|--------------------|------------------------|------------------------------------------------|
| `GEMINI_API_KEY`   | *(required)*           | https://aistudio.google.com                    |
| `GEMINI_CHAT_MODEL`| `gemini-2.0-flash`     |                                                |
| `GEMINI_EMBED_MODEL`| `gemini-embedding-001`|                                                |
| `USE_LLM_ROUTER`   | `false`                | `true` → LLM classifies intent (vs keywords)   |
| `CORS_ORIGINS`     | localhost:5173,...     | comma-separated                                |
| `MAX_HISTORY_PER_SESSION` | 20              | ring-buffer size                               |
| `TOP_K`            | 3                      | retrieved chunks per query                     |

## Dev notes

- Legacy `main.py` and `api/routes.py` still work (`main:app` resolves to
  the new app). New work should import from `app.*`.
- Session store is in-memory. For production, swap `SessionStore` in
  `app/services/session_service.py` for a Redis- or Postgres-backed
  implementation — the public interface is small enough that no caller
  needs to change.
- The `CorrelationMiddleware` echoes `X-Correlation-ID` on every response.
  Pass that header in from the client and your logs line up end-to-end.
