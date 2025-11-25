# Backend Implementation Prompt

## Goal
Deliver the FastAPI/LangChain backend described in `../ARCHITECTURE.md`, covering ingestion, retrieval, auth, persistence, and observability.

## Micro Tasks
1. **Environment & Tooling**
   - Finalize `.env` variables, Pydantic settings, logging config, and shared constants.
   - Wire lint/test tooling (ruff/mypy/pytest) and pre-commit hooks.
2. **DB Schema & Models**
   - Create SQLAlchemy models + Alembic migrations for `users`, `documents`, `document_chunks`, `document_embeddings`, `chat_sessions`, `chat_messages`.
   - Include fields for status, raw file path, checksum, and auditing timestamps.
3. **Auth & User Management**
   - Implement JWT signup/login routes, password hashing, token issuance, and FastAPI dependency that injects the current user.
   - Enforce user scoping across document + chat queries.
4. **File Storage Layer**
   - Implement storage helpers that persist raw uploads to `/storage/files` (or S3) with checksum + size validation.
   - Add lifecycle hooks for deletion and reprocessing.
5. **Ingestion Pipeline**
   - Build `/api/upload` endpoint accepting multiple files, validating MIME types + size.
   - Parse text (txt/pdfs), generate chunks via `RecursiveCharacterTextSplitter`, enqueue background embedding jobs with retry/backoff.
   - Persist document metadata/status updates throughout the pipeline.
6. **Vector Store Integration**
   - Initialize Chroma client with per-user collections or metadata filters.
   - Store embedding IDs in `document_embeddings` for clean deletion; support drop/rebuild flows.
7. **Retriever + `/api/ask`**
   - Configure LangChain retriever + LLM (OpenAI/Gemini) chain with system prompt template.
   - `/api/ask` should retrieve scoped chunks, call LLM, log latency, and persist chat history + sources.
8. **Documents Listing & Management**
   - `/api/docs` returns paginated docs with chunk counts, statuses, last processed timestamps, and links to raw files.
   - Add endpoints for deleting/reprocessing documents (bonus).
9. **Observability & Resilience**
   - Emit structured logs for ingestion stages and QA requests; add Prometheus-compatible metrics or counters.
   - Handle provider errors with retries + surface clear API errors.
10. **Testing & Docs**
    - Write pytest coverage for ingestion services, vector integration (mocked), auth flows, and API routes with httpx AsyncClient.
    - Update `backend/README.md` with any new run instructions, migrations, or troubleshooting tips.
