from pydantic import BaseModel, Field


class TitleRequest(BaseModel):
    context: str = Field(..., min_length=5)


class TitleResponse(BaseModel):
    title: str
