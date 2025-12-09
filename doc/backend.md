# Backend Service

## Overview

The backend (see `backend/app`) is a FastAPI 0.110+ application that manages ingestion of reference documents, builds embeddings, stores metadata in Postgres/SQLite, and exposes Retrieval-Augmented Generation endpoints. It uses SQLAlchemy 2.x ORM, Pydantic v2 models, and an optional ChromaDB vector store (embedded or HTTP).

Key entrypoints:

- `backend/app/main.py` – FastAPI app factory, CORS, startup hooks.
- `backend/app/api/router.py` – Registers feature routers (`auth`, `upload`, `docs`, `ask`, `health`).
- `backend/app/services` – File storage, text extraction, embeddings, vector store, RAG orchestration, auth helpers.

## Installation & Local Dev

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # set API keys, DB URL, secrets
uvicorn app.main:app --reload
```

By default the app runs on `http://127.0.0.1:8000` and uses SQLite + persistent Chroma under `backend/storage/`.

## Core Technologies

| Concern            | Library / Service |
| ------------------ | ----------------- |
| Web framework      | FastAPI + Uvicorn |
| ORM / DB layer     | SQLAlchemy 2.x    |
| Settings           | Pydantic Settings |
| Auth               | `python-jose`, `passlib[bcrypt]` |
| Vector search      | ChromaDB (embedded or HTTP) |
| RAG pipeline       | LangChain `RecursiveCharacterTextSplitter`, custom services |
| LLM providers      | OpenAI + Gemini SDKs with deterministic fallbacks |

## Directory Layout

- `app/api/routes` – HTTP handlers for auth/login (`auth.py`), uploads (`upload.py`), document management (`docs.py`), chat/title generation (`ask.py`), and health checks (`health.py`). All routes rely on FastAPI dependencies for DB sessions and JWT auth.
- `app/services` – Re-usable helpers such as:
  - `rag.py` orchestrating ingestion, chunking, embedding, and answering via LLM (`build_rag_service()` caches a configured instance).
  - `file_storage.py` saving uploads to `UPLOADS_DIR` with UUID filenames.
  - `text_processing.py` extracting text from `.txt`/`.pdf` via `pypdf`.
  - `embedding.py` selecting OpenAI embeddings or deterministic local hashes.
  - `vector_store.py` wrapping Chroma `PersistentClient` or `HttpClient`.
  - `llm.py` calling OpenAI/Gemini chat completions or returning deterministic answers.
  - `auth.py` hashing passwords, issuing JWT/refresh tokens, persisting refresh metadata.
- `app/models` – SQLAlchemy ORM models for `User`, `Document`, `DocumentChunk`.
- `app/schemas` – Pydantic response/request models (AskRequest, UploadResponse, Token, etc.).
- `app/db` – Engine/session builders and dependency helpers.
- `storage/` – Bound volume for uploads, embeddings, SQLite DB (mounted inside Docker).

## Configuration

Settings are defined in `backend/app/core/config.py` and read via environment variables (see `backend/.env.example`). Important ones:

- `DATABASE_URL` – SQLAlchemy URL (`sqlite:///./storage/nixai.db` locally, `postgresql+psycopg://...` in Compose).
- `CHROMA_PERSIST_DIR`, `UPLOADS_DIR` – Paths for embeddings + uploaded files.
- `CHROMA_SERVER_HOST/PORT/SSL` – When set, `VectorStoreService` uses Chroma’s HTTP API instead of the embedded client.
- `OPENAI_API_KEY`, `GEMINI_API_KEY`, `CHAT_MODEL`, `GEMINI_CHAT_MODEL`, `EMBEDDING_MODEL` – Control external providers.
- `JWT_SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_MINUTES` – Token settings.
- `BACKEND_CORS_ORIGINS` – Comma-separated list or JSON array consumed by `split_cors_origins`.

## APIs

All endpoints are nested under `/api`. Highlights:

| Method | Path | Description |
| ------ | ---- | ----------- |
| `POST` | `/api/auth/signup` | Create user with email + password. |
| `POST` | `/api/auth/login` | Returns JWT access + refresh tokens. |
| `POST` | `/api/auth/refresh` | Exchange refresh for new tokens. |
| `POST` | `/api/auth/logout` | Revoke refresh token. |
| `POST` | `/api/upload` | Auth required; accepts multipart files, extracts text, chunks, embeds into Chroma, stores metadata. |
| `GET`  | `/api/docs` | List documents for the authenticated user. |
| `DELETE` | `/api/docs/{document_id}` | Remove document, chunks, embeddings. |
| `POST` | `/api/ask` | Ask a question; service retrieves top-k chunks and generates answer via `LLMService`. |
| `POST` | `/api/ask/title` | Produce <=6-word summary title for a chat context. |
| `GET` | `/api/health/` | Liveness/readiness timestamp. |

## Data Flow

1. **Upload** – Files saved via `FileStorageService`, text extracted (`TextExtractionService`).
2. **Chunk & Embed** – LangChain splitter produces overlapping chunks, `EmbeddingService` creates vectors, `VectorStoreService` upserts embeddings with metadata.
3. **Persist** – Document + chunk models inserted into Postgres/SQLite, referencing stored paths and chunk counts.
4. **Query** – Questions hashed into query embeddings, Chroma returns top matches filtered by `user_id`.
5. **LLM Answer** – `LLMService` builds a prompt from retrieved context and calls OpenAI/Gemini; fallback returns deterministic message if no API keys.

## Docker & Deployment

- `backend/Dockerfile` installs dependencies, copies `app/`, seeds `.env`, creates storage folders, and runs `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- In `docker-compose.yml`, the backend service is built from that Dockerfile, mounts `backend_storage:/usr/src/backend/storage`, and sets `DATABASE_URL` to the Postgres container while still allowing overrides for external Chroma.

## Testing

Run `pytest` from the `backend` directory. Add unit tests inside `backend/tests` (not yet populated). Consider integrating against SQLite for fast runs and mocking vector/LLM calls to avoid external dependencies.
