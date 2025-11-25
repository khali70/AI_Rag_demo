📌 The Challenge

## 1️⃣ Step 1 – Knowledge Ingestion (Backend)

Create an API that:

Accepts multiple .txt or .pdf files via upload.

Extracts text content.

Splits and stores embeddings in a vector database (e.g., Chroma, FAISS, or Pinecone).

Use LangChain’s text splitters and embedding models (e.g., OpenAI embeddings).

Endpoints:

POST /api/upload → upload files and process them

GET /api/docs → list uploaded docs with metadata (name, chunks, embedding count)

## 2️⃣ Step 2 – Ask the Assistant (Backend)

Expose an endpoint:

POST /api/ask → { "question": "..." }

Uses LangChain Retriever + LLM Chain to:

Retrieve relevant chunks

Generate an answer using OpenAI API (or mock response if needed)

Return: { "answer": "...", "sources": [...] }

## 3️⃣ Step 3 – Web Dashboard (Frontend)

Build a simple dashboard using Next.js (App Router) that allows users to:

Upload documents

See processed docs and embeddings count

Ask questions via chat-like interface

Show model responses + sources

Use:

TailwindCSS

React Query / SWR for data fetching

Minimal but clean UI and responsive layout

## 4️⃣ Step 4 – Authentication (Optional but Bonus)

Implement basic login/signup flow with JWT or NextAuth.
Users should see only their own uploaded docs and chat history.

🗄️ Suggested Tech Stack
Backend : FastAPI + LangChain

Frontend : Next.js 14 (React 19)

Database : PostgreSQL / SQLite

Vector DB: Chroma / FAISS / Pinecone

Auth: JWT / NextAuth

Infra: Docker Compose

Docs: Swagger + README.md

🧩 Example API Flow
User uploads a file → /api/upload

Server extracts text + embeddings → saves to DB

User asks a question → /api/ask

Backend retrieves top chunks → generates answer

Frontend displays the full Q&A flow

🎁 Bonus Points
✨ Docker Compose (API + DB + Vector Store)

✨ Persistent chat history per user

✨ Swagger + OpenAPI docs

✨ Retry logic & async background tasks

✨ Unit tests for retriever & routes

✨ “Source viewer” UI (click to expand retrieved docs)

🧰 What You Should Submit
📂 GitHub Repository with:

Organized code: /backend, /frontend, /docs

README.md with setup steps

docker-compose.yml for local run

Optional ARCHITECTURE.md with diagram
