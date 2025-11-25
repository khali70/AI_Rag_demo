# Implementation Prompt

## Goal
Build the NixAI document-ingestion + QA assistant as described in `instructions.md` and `ARCHITECTURE.md`, delivering FastAPI/LangChain backend plus Next.js dashboard with authentication and optional extras.

## Micro Tasks
1. **Repo Setup**
   - Configure shared tooling (`.editorconfig`, linters, `docker-compose.yml` with api/frontend/db/vector).
   - Add root `README.md` + `.env.example` documenting OpenAI + DB creds.
2. **Backend Scaffolding**
   - Bootstrap FastAPI project structure (`app/main.py`, routers, settings, dependencies).
   - Configure SQLAlchemy models for users, documents, document_chunks, chat sessions/messages; run initial migration.
3. **Authentication Layer**
   - Implement JWT signup/login endpoints, password hashing, dependency for authenticated requests.
   - Wire middleware/guards so `/api/upload`, `/api/docs`, `/api/ask` require a valid user.
4. **Document Ingestion Pipeline**
   - Implement `/api/upload` (multipart) accepting multiple `.txt/.pdf`.
   - Parse text (txt, pdf), split via LangChain `RecursiveCharacterTextSplitter`, embed with `OpenAIEmbeddings`, persist metadata in Postgres + embeddings in Chroma.
   - Offload heavy work to FastAPI background task or Celery worker; emit status + chunk counts.
5. **Document Listing Endpoint**
   - Implement `/api/docs` that returns per-user documents with metadata (filename, status, chunk_count, embedding_count, timestamps).
   - Ensure filtering + pagination if needed.
6. **Retriever + QA Endpoint**
   - Configure Chroma retriever + LLM chain (OpenAI or mock fallback).
   - Implement `/api/ask` accepting `{question, session_id?}` returning `{answer, sources}` and persisting chat history.
   - Add unit tests for retriever logic + API schema validation.
7. **Frontend Foundation**
   - Initialize Next.js 14 App Router project with Tailwind + React Query provider + auth context (NextAuth or custom JWT storage).
   - Implement login/signup screens with form validation.
8. **Dashboard – Documents**
   - Build upload UI (drag-and-drop, file list, progress) hitting `/api/upload`.
   - Display table of ingested docs with status + embedding counts, expandable “source viewer”.
9. **Chat Interface**
   - Create chat page with session selector, message list, streaming answer display, and inline source chips linking to docs.
   - Integrate with `/api/ask`, handle loading/error states, persist sessions client-side and via backend.
10. **Polish & Extras**
    - Add Swagger docs, README instructions, Docker scripts, and CI checks.
    - Bonus: retry logic for embeddings, analytics, unit/E2E tests, background worker monitoring.
