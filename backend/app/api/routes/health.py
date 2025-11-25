from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Health check")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
