from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

import chromadb
from chromadb import Settings as ChromaSettings

from ..core.config import Settings
from ..models.document import Document, DocumentChunk


@dataclass
class SourceChunk:
    chunk_id: str
    document_id: str
    document_name: str
    chunk_index: int
    content: str
    score: float | None = None


class VectorStoreService:
    """Wrapper around ChromaDB for persisting and retrieving embeddings."""

    def __init__(self, settings: Settings) -> None:
        self._using_http = bool(settings.chroma_server_host)
        telemetry_settings = ChromaSettings(allow_reset=True, anonymized_telemetry=False)

        if self._using_http:
            self._client = chromadb.HttpClient(
                host=settings.chroma_server_host,
                port=settings.chroma_server_port,
                ssl=settings.chroma_server_ssl,
                settings=telemetry_settings,
            )
        else:
            path = Path(settings.chroma_persist_dir).expanduser()
            path.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=str(path),
                settings=telemetry_settings,
            )
        self._collection = self._client.get_or_create_collection(name="documents")

    def upsert_document_chunks(
        self,
        document: Document,
        chunks: Sequence[DocumentChunk],
        embeddings: Sequence[List[float]],
        user_id: str,
    ) -> None:
        if not chunks or not embeddings:
            return

        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings length mismatch")

        self._collection.delete(where={"document_id": document.id})

        self._collection.add(
            ids=[chunk.id for chunk in chunks],
            embeddings=list(embeddings),
            documents=[chunk.content for chunk in chunks],
            metadatas=[
                {
                    "document_id": document.id,
                    "document_name": document.filename,
                    "chunk_index": chunk.chunk_index,
                    "user_id": user_id,
                }
                for chunk in chunks
            ],
        )
        if hasattr(self._client, "persist"):
            self._collection.persist()

    def query(self, user_id: str, query_embedding: List[float], limit: int = 4) -> List[SourceChunk]:
        if not query_embedding:
            return []

        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where={"user_id": user_id},
            )
        except Exception:  # pragma: no cover - Chroma raises custom errors
            return []

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0] if "distances" in results else None

        sources: list[SourceChunk] = []
        for idx, chunk_id in enumerate(ids):
            metadata = metadatas[idx] if idx < len(metadatas) else {}
            sources.append(
                SourceChunk(
                    chunk_id=chunk_id,
                    document_id=str(metadata.get("document_id")),
                    document_name=str(metadata.get("document_name", "unknown")),
                    chunk_index=int(metadata.get("chunk_index", 0)),
                    content=documents[idx] if idx < len(documents) else "",
                    score=distances[idx] if distances and idx < len(distances) else None,
                )
            )
        return sources

    def delete_document_embeddings(self, document_id: str) -> None:
        try:
            self._collection.delete(where={"document_id": document_id})
            if hasattr(self._client, "persist"):
                self._collection.persist()
        except Exception:
            # Swallow Chroma errors; downstream code can continue.
            pass
