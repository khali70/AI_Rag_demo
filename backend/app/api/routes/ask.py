from fastapi import APIRouter, HTTPException, status

from ...core.config import get_settings
from ...schemas import AskRequest, AskResponse
from ...services.rag import build_rag_service

router = APIRouter()

rag_service = build_rag_service()
settings = get_settings()


@router.post("/", response_model=AskResponse, summary="Ask a question against uploaded docs.")
async def ask_question(payload: AskRequest) -> AskResponse:
    if not payload.question.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question cannot be empty.")

    return await rag_service.answer_question(payload.question, settings.default_user_id)
