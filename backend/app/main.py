from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import api_router
from .core.config import get_settings
from .db.session import Base, engine

# Ensure SQLAlchemy models are registered before metadata creation.
from . import models as _  # noqa: F401


def create_application() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title=settings.app_name, version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup_event() -> None:
        Base.metadata.create_all(bind=engine)

    app.include_router(api_router, prefix="/api")

    return app


app = create_application()
