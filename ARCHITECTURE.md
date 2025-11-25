# NixAI – System Architecture

## 1. Solution Overview
- **Goal:** Enable users to upload reference documents, embed their contents, and query an assistant that responds with grounded answers + cited sources.
- **Core split:** `backend/` (FastAPI, LangChain, Postgres, Chroma) and `frontend/` (Next.js 14 App Router, Tailwind, React Query).
- **Key flows:** document ingestion (`/api/upload`), document listing (`/api/docs`), and retrieval augmented answering (`/api/ask`).

## 2. Backend Architecture (FastAPI)
| Concern | Details |
| --- | --- |
| **Framework** | FastAPI with Pydantic models, async endpoints, and dependency-injected services. |
| **Modules** | `ingestion` (file parsing, LangChain text splitters, embedding pipeline, queue workers), `retrieval` (vector store retriever + LLM chain), `persistence` (SQLAlchemy/PostgreSQL tables for users, documents, document_chunks, chats), `api` (routers + schemas), `auth` (JWT via fastapi-users or custom), `files` (blob storage helpers). |
| **Storage** | PostgreSQL (metadata, auth, chat history), Chroma vector store persisted to disk volume (per-user collections), and raw file storage (local disk bucket `/storage/files` or S3-compatible service). |
| **Embeddings** | LangChain `OpenAIEmbeddings` + optional Gemini via `langchain-google-genai`, using `RecursiveCharacterTextSplitter`. Each chunk stored both in SQL (for metadata) and Chroma with doc/user metadata tags. |
| **File handling** | Upload endpoint accepts multiple `.txt` / `.pdf`. PDFs parsed with `pypdf`. Files streamed to temp dir, validated, then persisted to blob storage for later reprocessing. Text extraction + chunking happen asynchronously; ingestion status tracked per document. |
| **Retrieval** | `/api/ask` builds a `RetrievalQA` chain: Chroma retriever scoped to `user_id` + `document_id` filter → OpenAI/Gemini LLM. Returns answer + source chunk metadata and raw file references. |
| **Docs listing** | `/api/docs` queries Postgres for per-user docs, chunk counts, embedding status. |
| **Observability** | Structured logging (loguru/cstandard) capturing file ingestion lifecycle + LLM latency, Prometheus-ready metrics (bonus), plus tracing hooks for embeddings + retriever calls.

### Backend Data Model (simplified)
- `users`: id, email, hashed_password, created_at.
- `documents`: id, user_id (FK), filename, mime_type, status, chunk_count, raw_path, checksum, created_at.
- `document_chunks`: id, document_id (FK), chunk_index, text, embedding_id (FK into Chroma metadata), token_count.
- `document_embeddings`: metadata table referencing Chroma collection name, vector_id, namespace/user scope for auditable deletes.
- `chat_sessions` (optional): id, user_id, title.
- `chat_messages`: id, session_id, role (`user`/`assistant`), content, sources.

### API Routes
| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/upload` | Authenticated upload (multipart). Stores raw files, emits ingestion job (FastAPI BackgroundTasks / Celery) to extract text + embeddings, returns doc metadata + status. |
| `GET` | `/api/docs` | Lists user docs with chunk + embedding counts, status flags. |
| `POST` | `/api/ask` | Accepts `{question, session_id?}`; retrieves top-k chunks, calls LLM; stores message in chat history; responds `{answer, sources}`. |
| `POST` | `/api/auth/signup` / `/login` | Optional bonus JWT auth. |

### Background & Reliability
- Embedding + text-extraction run in background workers (FastAPI `BackgroundTasks` for MVP, Celery/RQ + Redis for scale). Each job includes retry policy (exponential backoff via Tenacity) to handle transient LLM/vector failures.
- Vector store scoped per user: each user gets a unique Chroma collection (`collection_{user_id}`) or shared collection with metadata filters; deletion routines remove both SQL + vector entries.
- Validation: unit tests for ingestion parser, retriever, and REST routes. Use pytest + httpx AsyncClient.
- Observability: ingestion + `/api/ask` log structured events (doc_id, user_id, latency). Optional OpenTelemetry spans exported to tracing backend.
- Docs: enable Swagger/OpenAPI, plus README walkthrough covering tenancy + storage behavior.

## 3. Frontend Architecture (Next.js 14 + Tailwind)
| Concern | Details |
| --- | --- |
| **Routing** | App Router with nested layouts; protected routes using middleware that checks JWT/NextAuth session. |
| **State/Data** | React Query for `/api/docs`, `/api/ask`, `/api/upload`. Toast notifications (e.g., React Hot Toast). |
| **UI** | TailwindCSS + Headless UI/Radix for accessible components. Key pages: `Dashboard` (upload + doc table), `Chat` (QA interface), `Auth`. |
| **Upload workflow** | Drag-and-drop uploader component -> POST `/api/upload` -> optimistic updates to docs list. |
| **Docs table** | Shows filename, size, status, chunk_count, embedding_count. Expandable row displays retrieved chunks (“source viewer”). |
| **Chat interface** | Streaming answer display, chips for cited sources, session selector (persistent history). |
| **Error & loading states** | React Query suspense, skeleton loaders, retry/backoff built-in. |

## 4. Authentication & Authorization
- Baseline: JWT auth (FastAPI `OAuth2PasswordBearer`) or NextAuth credentials provider hitting backend.
- Each request includes `Authorization: Bearer <token>`; backend enforces `user_id` scoping for documents/chats.
- Refresh tokens (bonus) stored HttpOnly cookies; access tokens short-lived.

## 5. Infrastructure & DevOps
- `docker-compose.yml` orchestrates: `api` (FastAPI + Uvicorn), `frontend` (Next.js dev server or production build), `db` (Postgres), `vector` (Chroma server or persistent volume), optional `redis` for background jobs.
- Shared `.env` + `.env.example` to describe secrets (DB, OpenAI API key, JWT secrets).
- CI suggestion: lint (ruff + mypy + eslint), tests (pytest, Playwright/React Testing Library).
- Deployment ready for Railway/Vercel/Render: backend containerized, frontend static export or Next server, Postgres managed service, vector store persistent disk.

## 6. Documentation Deliverables
- `README.md`: setup, env vars, run via Docker, API usage.
- `ARCHITECTURE.md` (this file) + optional diagrams (Mermaid or Excalidraw).
- `prompt.md`: granular implementation tasks / prompt for execution.
