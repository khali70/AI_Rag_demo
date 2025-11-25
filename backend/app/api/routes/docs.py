from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.config import get_settings
from ...db.deps import get_db
from ...schemas import DocumentListResponse, DocumentSummary
from ...services.rag import build_rag_service

router = APIRouter()

rag_service = build_rag_service()
settings = get_settings()


@router.get("/", response_model=DocumentListResponse, summary="List uploaded documents.")
async def list_documents(db: Session = Depends(get_db)) -> DocumentListResponse:
    documents = rag_service.list_documents(db, settings.default_user_id)
    summaries = [DocumentSummary.model_validate(doc) for doc in documents]
    return DocumentListResponse(documents=summaries)
