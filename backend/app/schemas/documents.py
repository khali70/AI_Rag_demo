from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentSummary(BaseModel):
    id: str = Field(..., description="Document identifier.")
    filename: str = Field(..., description="Original filename.")
    content_type: str = Field(..., description="MIME type detected for the document.")
    chunk_count: int = Field(..., description="Number of text chunks for this document.")
    embedding_count: int = Field(..., description="Number of embeddings stored for this document.")
    created_at: datetime = Field(..., description="Upload timestamp.")

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    documents: list[DocumentSummary]


class UploadResponse(BaseModel):
    documents: list[DocumentSummary]
    count: int
