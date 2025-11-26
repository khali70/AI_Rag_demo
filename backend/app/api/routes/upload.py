from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ...db.deps import get_db
from ...schemas import UploadResponse
from ...api.routes.auth import get_current_user_id
from ...services.rag import build_rag_service
from ...services.text_processing import TextExtractionError

router = APIRouter()

rag_service = build_rag_service()


@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and ingest multiple documents.",
)
async def upload_documents(
    files: list[UploadFile] = File(..., description="List of .txt or .pdf files."),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> UploadResponse:
    try:
        return await rag_service.ingest_uploads(files, db, user_id)
    except (TextExtractionError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:  # pragma: no cover - general safeguard
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
