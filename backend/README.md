# Backend

NixAI's backend is an async FastAPI service that ingests reference documents, stores their metadata + embeddings, and exposes retrieval-augmented question answering APIs.

## Project layout
- `app/main.py` – FastAPI application factory.
- `app/api` – routers for `/api/upload`, `/api/docs`, `/api/ask`, `/api/health`.
- `app/services` – ingestion pipeline (file storage, text extraction, embeddings, vector store, LLM wrapper).
- `app/models` – SQLAlchemy ORM models (`Document`, `DocumentChunk`).
- `app/schemas` – Pydantic response/request models.
- `app/db` – SQLAlchemy session helpers.

## Requirements
- Python 3.11+
- Node/Postgres/Chroma are optional; by default the app uses SQLite + embedded Chroma persistence.

Install dependencies once:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # update secrets (OpenAI key, DB URL, etc.)
```

## Running locally
```bash
uvicorn app.main:app --reload
```

The API will be available at http://127.0.0.1:8000 with interactive docs at `/docs`.

### Core endpoints
| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/health/` | Simple readiness probe. |
| `POST` | `/api/upload` | Accepts multiple `.txt`/`.pdf` files, extracts text, chunks, embeds via LangChain, and indexes into Chroma. Returns document metadata. |
| `GET` | `/api/docs` | Lists documents for the current (demo) user with chunk + embedding counts. |
| `POST` | `/api/ask` | `{ "question": "..." }` → retrieves top chunks from Chroma, calls LLM (OpenAI if available, deterministic fallback otherwise), returns `answer` + `sources`. |

## Testing
```bash
pytest
```
Add your own tests under `backend/tests`.

## Configuration
All configuration is handled via environment variables (`.env`). Important ones:
- `DATABASE_URL`: defaults to SQLite for simplicity.
- `OPENAI_API_KEY`: if set, embeddings + answers use OpenAI; otherwise deterministic offline implementations are used.
- `BACKEND_CORS_ORIGINS`: JSON array or comma-separated list of frontend origins (defaults to `http://localhost:3000` and `http://127.0.0.1:3000`).
- `CHAT_MODEL` / `GEMINI_CHAT_MODEL`: choose valid model identifiers for the LLM provider you enable (`OPENAI_API_KEY` or `GEMINI_API_KEY`).
- `CHROMA_PERSIST_DIR`, `UPLOADS_DIR`: directories for vector store + original files (created automatically).
- `CHROMA_SERVER_HOST`, `CHROMA_SERVER_PORT`: set these if you prefer using a networked Chroma service (e.g., via Docker) instead of the embedded persistent client.
