from fastapi import APIRouter, Depends, HTTPException, status

from ...schemas import AskRequest, AskResponse
from ...services.rag import build_rag_service
from .auth import get_current_user_id

router = APIRouter()

rag_service = build_rag_service()


@router.post("/", response_model=AskResponse, summary="Ask a question against uploaded docs.")
async def ask_question(payload: AskRequest, user_id: str = Depends(get_current_user_id)) -> AskResponse:
    if not payload.question.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question cannot be empty.")

    return await rag_service.answer_question(payload.question, user_id)
