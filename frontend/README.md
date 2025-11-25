# Frontend

Next.js 14 (App Router) dashboard for uploading documents and chatting with the RAG backend.

## Setup
```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_BASE_URL` to your backend API (defaults to `http://localhost:8000/api`).

## Pages
- `/documents` – upload files + view processed docs.
- `/chat` – ask questions, see answers + cited sources.
