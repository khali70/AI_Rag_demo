from fastapi import APIRouter

from .routes import ask, auth, docs, health, upload

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(upload.router, prefix="/upload", tags=["documents"])
api_router.include_router(docs.router, prefix="/docs", tags=["documents"])
api_router.include_router(ask.router, prefix="/ask", tags=["chat"])
