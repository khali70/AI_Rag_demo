from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool

from ...core.config import get_settings
from ...schemas import AskRequest, AskResponse, TitleRequest, TitleResponse
from ...services.llm import LLMService
from ...services.rag import build_rag_service
from .auth import get_current_user_id

router = APIRouter()

rag_service = build_rag_service()
llm_service = LLMService(get_settings())


@router.post("/", response_model=AskResponse, summary="Ask a question against uploaded docs.")
async def ask_question(payload: AskRequest, user_id: str = Depends(get_current_user_id)) -> AskResponse:
    if not payload.question.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question cannot be empty.")

    return await rag_service.answer_question(payload.question, user_id)


@router.post("/title", response_model=TitleResponse, summary="Generate a chat title.")
async def generate_title(payload: TitleRequest) -> TitleResponse:
    title = await run_in_threadpool(llm_service.generate_title, payload.context)
    return TitleResponse(title=title or "Chat session")
