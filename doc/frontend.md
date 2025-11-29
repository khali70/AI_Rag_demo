# Frontend Application

## Overview

The frontend (`frontend/`) is a Next.js 14 App Router dashboard that lets users upload documents, browse processed files, and chat with the backend’s RAG API. It uses React 18, TypeScript, Tailwind CSS, and React Query for data fetching/caching.

## Installation & Local Dev

```bash
cd frontend
npm install
npm run dev
```

The dev server runs at `http://localhost:3000`. Set `NEXT_PUBLIC_API_BASE_URL` (defaults to `http://localhost:8000/api`) so the browser calls the correct backend.

## Build & Production

- `npm run build` – Compiles the App Router project for production.
- `npm run start` – Serves the built app (used in Docker runner stage).
- Docker builds (`frontend/Dockerfile`) use multi-stage builds (`deps`, `builder`, `runner`), inject `NEXT_PUBLIC_API_BASE_URL` at build time, copy `.next` output into a `node:20-alpine` runtime, and run `next start`.
- In `docker-compose.yml`, the frontend reads `API_INTERNAL_BASE_URL` at runtime so server components can call `http://backend:8000/api` inside the Docker network.

## Key Dependencies

| Package | Purpose |
| ------- | ------- |
| `next@14.1.0` | App Router, server actions, routing. |
| `@tanstack/react-query` | Client-side caching for fetch calls. |
| `tailwindcss`, `postcss`, `autoprefixer` | Styling pipeline. |
| `uuid` | Generating stable IDs (e.g., for optimistic updates). |

## Directory Layout

- `app/` – App Router tree:
  - `layout.tsx` – Root layout wiring up fonts, metadata, and providers.
  - `page.tsx` – Landing/dashboard entry.
  - `auth/` – Auth routes (login/signup forms consuming `/api/auth`).
  - `documents/` – Upload UI plus processed document list (hooks into `/api/upload` and `/api/docs`).
  - `chat/` – Chat interface that posts to `/api/ask` and renders RAG answers with source citations.
  - `globals.css` – Tailwind base styles.
  - `not-found.tsx` – 404 boundary.
- `components/`:
  - `providers.tsx` – Wraps React Query + global context providers.
  - `auth-guard.tsx` – Client component enforcing auth on protected pages.
  - `auth-menu.tsx` – Displays user menu / logout.
- `lib/api.ts` – Fetch helpers that centralize `API_INTERNAL_BASE_URL` logic and handle token headers.
- `next.config.mjs`, `tailwind.config.js`, `tsconfig.json` – Framework configuration.

## Environment Variables

| Variable | Scope | Description |
| -------- | ----- | ----------- |
| `NEXT_PUBLIC_API_BASE_URL` | Build-time + client runtime | Public backend URL inserted into the bundle (e.g., `https://api.example.com/api`). Must include `/api`. |
| `API_INTERNAL_BASE_URL` | Runtime (server components/Docker) | Internal URL for SSR/server actions when running behind Docker; defaults to `http://backend:8000/api`. |

All variables prefixed with `NEXT_PUBLIC_` are exposed to the browser; keep secrets server-side only.

## Authentication Flow

1. Auth pages capture credentials and call backend `/api/auth/login` or `/api/auth/signup`.
2. Access tokens are stored client-side (e.g., React Query cache or context) and attached to subsequent fetches.
3. Protected pages/components use `AuthGuard` to redirect unauthenticated visitors to the login screen.

## Document Upload & Chat UX

- The documents page allows selecting multiple `.txt`/`.pdf` files, calls the backend upload endpoint, then displays returned metadata (filename, created date, chunk counts).
- The chat page posts questions to `/api/ask`, renders streaming/complete responses, and surfaces the retrieved `sources` list for transparency (document name, chunk index, snippet).

## Testing & Linting

- `npm run lint` – Runs Next.js ESLint config (TypeScript-aware).
- You can add component tests with your preferred stack (e.g., Jest + React Testing Library) if needed; not currently included.

## Deployment Notes

- When deploying with the provided compose stack (`./scripts/deploy.sh up`), frontend traffic hits `localhost:3000` and proxies to the backend via `NEXT_PUBLIC_API_BASE_URL`.
- For custom hosting (Vercel, container platform), ensure environment variables match your backend ingress URL, and that HTTPS/TLS is configured accordingly.
