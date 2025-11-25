from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)
    chat_session_id: str | None = Field(
        default=None, description="Optional session identifier for future multi-turn chat support."
    )


class SourceInfo(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    chunk_index: int
    score: float | None = None
    snippet: str


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]
