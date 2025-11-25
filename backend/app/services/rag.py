from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Sequence

from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session

from ..core.config import Settings, get_settings
from ..models.document import Document, DocumentChunk
from ..schemas import AskResponse, DocumentSummary, SourceInfo, UploadResponse
from .embedding import EmbeddingService
from .file_storage import FileStorageService
from .llm import LLMService
from .text_processing import TextExtractionError, TextExtractionService
from .vector_store import VectorStoreService


class RAGService:
    """Coordinates file ingestion + retrieval augmented answering."""

    def __init__(
        self,
        settings: Settings,
        file_storage: FileStorageService,
        text_extractor: TextExtractionService,
        embedding_service: EmbeddingService,
        vector_store: VectorStoreService,
        llm_service: LLMService,
    ) -> None:
        self.settings = settings
        self.file_storage = file_storage
        self.text_extractor = text_extractor
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm_service = llm_service
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.text_splitter_chunk_size,
            chunk_overlap=settings.text_splitter_chunk_overlap,
        )

    async def ingest_uploads(self, uploads: Sequence[UploadFile], db: Session, user_id: str) -> UploadResponse:
        if not uploads:
            raise ValueError("No files supplied.")

        stored_documents: list[DocumentSummary] = []

        for upload in uploads:
            document = await self._process_upload(upload, db, user_id)
            stored_documents.append(DocumentSummary.model_validate(document))

        stored_documents.sort(key=lambda doc: doc.created_at, reverse=True)
        return UploadResponse(documents=stored_documents, count=len(stored_documents))

    async def _process_upload(self, upload: UploadFile, db: Session, user_id: str) -> Document:
        metadata = await self.file_storage.save_upload(upload)
        text = await run_in_threadpool(
            self.text_extractor.extract_text,
            Path(metadata["storage_path"]),
            metadata["content_type"],
        )

        if not text.strip():
            raise TextExtractionError(f"No text found in {metadata['original_name']}")

        chunks = await run_in_threadpool(self.text_splitter.split_text, text)
        if not chunks:
            raise TextExtractionError(f"Unable to split text for {metadata['original_name']}")

        embeddings = await run_in_threadpool(self.embedding_service.embed_documents, chunks)

        document = Document(
            user_id=user_id,
            filename=metadata["original_name"],
            content_type=metadata["content_type"],
            stored_path=metadata["storage_path"],
            size_bytes=metadata["size_bytes"],
            chunk_count=len(chunks),
            embedding_count=len(embeddings),
        )

        chunk_models: list[DocumentChunk] = []

        try:
            db.add(document)
            db.flush()

            for index, chunk_text in enumerate(chunks):
                chunk_model = DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk_text,
                    token_count=len(chunk_text.split()),
                )
                db.add(chunk_model)
                chunk_models.append(chunk_model)

            db.commit()
            db.refresh(document)
        except Exception:
            db.rollback()
            raise

        await run_in_threadpool(self.vector_store.upsert_document_chunks, document, chunk_models, embeddings, user_id)

        return document

    def list_documents(self, db: Session, user_id: str) -> list[Document]:
        return (
            db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .all()
        )

    async def answer_question(self, question: str, user_id: str, top_k: int = 4) -> AskResponse:
        query_embedding = await run_in_threadpool(self.embedding_service.embed_query, question)
        source_chunks = await run_in_threadpool(self.vector_store.query, user_id, query_embedding, top_k)

        context = "\n\n".join(
            f"[{chunk.document_name}#{chunk.chunk_index}] {chunk.content}" for chunk in source_chunks
        )

        answer = await run_in_threadpool(self.llm_service.generate_answer, question, context)

        sources = [
            SourceInfo(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                document_name=chunk.document_name,
                chunk_index=chunk.chunk_index,
                score=chunk.score,
                snippet=chunk.content[:400],
            )
            for chunk in source_chunks
        ]

        return AskResponse(answer=answer, sources=sources)


@lru_cache
def build_rag_service() -> RAGService:
    """Factory used by FastAPI dependencies."""
    settings = get_settings()
    return RAGService(
        settings=settings,
        file_storage=FileStorageService(settings.uploads_dir),
        text_extractor=TextExtractionService(),
        embedding_service=EmbeddingService(settings),
        vector_store=VectorStoreService(settings),
        llm_service=LLMService(settings),
    )
