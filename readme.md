<video controls src="doc/nexAI.mp4" title="demo"></video>

## Production stack

The repository ships with a Docker-based deployment that runs Postgres, the FastAPI backend, and the Next.js frontend. A helper script wraps the `docker compose` commands so you can bring the stack up consistently.

### Prerequisites

- Docker Engine + Docker Compose Plugin
- `backend/.env` populated with your secrets (`cp backend/.env.example backend/.env` is a good starting point)

### Quick start

```bash
./scripts/deploy.sh up
```

This command:

- Builds the backend (`backend/Dockerfile`) and frontend (`frontend/Dockerfile`) images.
- Starts the Postgres database, backend API, frontend app, and (optionally) the Chroma vector store.
- Exposes the backend at `http://localhost:8000` and the frontend at `http://localhost:3000`.

### Script options

- `./scripts/deploy.sh --no-chroma` – Skip the Chroma container and use the backend’s embedded persistent store.
- `./scripts/deploy.sh --attach` – Run `docker compose up` in the foreground (handy while debugging).
- `./scripts/deploy.sh --no-build` – Start the stack without rebuilding images.
- `./scripts/deploy.sh down` – Stop and remove the containers.
- `./scripts/deploy.sh logs` – Tail the backend + frontend logs.

Under the hood the script exports a few helpful environment variables before invoking Docker Compose:

- `NEXT_PUBLIC_API_BASE_URL` – Controls the public API endpoint baked into the frontend build (defaults to `http://localhost:8000/api`).
- `API_INTERNAL_BASE_URL` – Internal URL the frontend uses at runtime to talk to the backend (`http://backend:8000/api` inside the compose network).
- `CHROMA_SERVER_HOST` / `CHROMA_SERVER_PORT` / `CHROMA_SERVER_SSL` – Override these to point the backend at an external Chroma instance if you are not running the bundled container.

You can always bypass the script and run Compose directly, e.g. `docker compose --profile chroma up -d --build`.
