from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ...core.config import get_settings
from ...db.deps import get_db
from ...schemas import UploadResponse
from ...services.rag import build_rag_service
from ...services.text_processing import TextExtractionError

router = APIRouter()

rag_service = build_rag_service()
settings = get_settings()


@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and ingest multiple documents.",
)
async def upload_documents(
    files: list[UploadFile] = File(..., description="List of .txt or .pdf files."),
    db: Session = Depends(get_db),
) -> UploadResponse:
    try:
        return await rag_service.ingest_uploads(files, db, settings.default_user_id)
    except (TextExtractionError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:  # pragma: no cover - general safeguard
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
