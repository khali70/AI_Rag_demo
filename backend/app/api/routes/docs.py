from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db.deps import get_db
from ...schemas import DocumentListResponse, DocumentSummary
from ...services.rag import build_rag_service
from .auth import get_current_user_id

router = APIRouter()

rag_service = build_rag_service()


@router.get("/", response_model=DocumentListResponse, summary="List uploaded documents.")
async def list_documents(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> DocumentListResponse:
    documents = rag_service.list_documents(db, user_id)
    summaries = [DocumentSummary.model_validate(doc) for doc in documents]
    return DocumentListResponse(documents=summaries)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a document.")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> None:
    deleted = rag_service.delete_document(db, document_id, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
