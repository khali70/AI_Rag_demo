# Backend

NixAI's backend is an async FastAPI service that ingests reference documents, stores their metadata + embeddings, and exposes retrieval-augmented question answering APIs.

## Project layout

- `app/main.py` – FastAPI application factory.
- `app/api` – routers for `/api/auth`, `/api/upload`, `/api/docs`, `/api/ask`, `/api/health`.
- `app/services` – ingestion pipeline (file storage, text extraction, embeddings, vector store, LLM wrapper, auth helpers).
- `app/models` – SQLAlchemy ORM models (`User`, `Document`, `DocumentChunk`).
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

| Method | Path             | Description                                                                                                                                                  |
| ------ | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GET`  | `/api/health/`   | Simple readiness probe.                                                                                                                                      |
| `POST` | `/api/auth/signup` | Register with email + password.                                                                                                                            |
| `POST` | `/api/auth/login`  | Log in with email + password, receive JWT access token.                                                                                                    |
| `POST` | `/api/upload`    | Auth required. Accepts multiple `.txt`/`.pdf` files, extracts text, chunks, embeds via LangChain, and indexes into Chroma. Returns document metadata.       |
| `GET`  | `/api/docs`      | Auth required. Lists documents for the current user with chunk + embedding counts.                                                                           |
| `POST` | `/api/ask`       | Auth required. `{ "question": "..." }` → retrieves top chunks from Chroma for the current user, calls LLM (OpenAI or Gemini if configured), returns answer + sources. |
| `POST` | `/api/ask/title` | Generate a short descriptive title for a chat session given the conversation context.                                                                        |

## Testing

```bash
pytest
```

Add your own tests under `backend/tests`.

## Configuration

All configuration is handled via environment variables (`.env`). Important ones:

- `DATABASE_URL`: defaults to SQLite for simplicity.
- `OPENAI_API_KEY`: if set, embeddings + answers use OpenAI; otherwise deterministic offline implementations are used.
- `BACKEND_CORS_ORIGINS`: JSON array, comma-separated list, or `"*"` to allow all origins (default is `"*"`).
- `CHAT_MODEL` / `GEMINI_CHAT_MODEL`: choose valid model identifiers for the LLM provider you enable (`OPENAI_API_KEY` or `GEMINI_API_KEY`).
- `CHROMA_PERSIST_DIR`, `UPLOADS_DIR`: directories for vector store + original files (created automatically).
- `CHROMA_SERVER_HOST`, `CHROMA_SERVER_PORT`: set these if you prefer using a networked Chroma service (e.g., via Docker) instead of the embedded persistent client.

### gemini models

- models/embedding-gecko-001
- models/gemini-2.5-pro-preview-03-25
- models/gemini-2.5-flash
- models/gemini-2.5-pro-preview-05-06
- models/gemini-2.5-pro-preview-06-05
- models/gemini-2.5-pro
- models/gemini-2.0-flash-exp
- models/gemini-2.0-flash
- models/gemini-2.0-flash-001
- models/gemini-2.0-flash-lite-001
- models/gemini-2.0-flash-lite
- models/gemini-2.0-flash-lite-preview-02-05
- models/gemini-2.0-flash-lite-preview
- models/gemini-2.0-pro-exp
- models/gemini-2.0-pro-exp-02-05
- models/gemini-exp-1206
- models/gemini-2.0-flash-thinking-exp-01-21
- models/gemini-2.0-flash-thinking-exp
- models/gemini-2.0-flash-thinking-exp-1219
- models/gemini-2.5-flash-preview-tts
- models/gemini-2.5-pro-preview-tts
- models/learnlm-2.0-flash-experimental
- models/gemma-3-1b-it
- models/gemma-3-4b-it
- models/gemma-3-12b-it
- models/gemma-3-27b-it
- models/gemma-3n-e4b-it
- models/gemma-3n-e2b-it
- models/gemini-flash-latest
- models/gemini-flash-lite-latest
- models/gemini-pro-latest
- models/gemini-2.5-flash-lite
- models/gemini-2.5-flash-image-preview
- models/gemini-2.5-flash-image
- models/gemini-2.5-flash-preview-09-2025
- models/gemini-2.5-flash-lite-preview-09-2025
- models/gemini-3-pro-preview
- models/gemini-3-pro-image-preview
- models/nano-banana-pro-preview
- models/gemini-robotics-er-1.5-preview
- models/gemini-2.5-computer-use-preview-10-2025
- models/embedding-001
- models/text-embedding-004
- models/gemini-embedding-exp-03-07
- models/gemini-embedding-exp
- models/gemini-embedding-001
- models/aqa
- models/imagen-4.0-generate-preview-06-06
- models/imagen-4.0-ultra-generate-preview-06-06
- models/imagen-4.0-generate-001
- models/imagen-4.0-ultra-generate-001
- models/imagen-4.0-fast-generate-001
- models/veo-2.0-generate-001
- models/veo-3.0-generate-001
- models/veo-3.0-fast-generate-001
- models/veo-3.1-generate-preview
- models/veo-3.1-fast-generate-preview
- models/gemini-2.0-flash-live-001
- models/gemini-live-2.5-flash-preview
- models/gemini-2.5-flash-live-preview
- models/gemini-2.5-flash-native-audio-latest
- models/gemini-2.5-flash-native-audio-preview-09-2025
