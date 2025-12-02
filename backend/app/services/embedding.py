from __future__ import annotations

import hashlib
import random
from typing import List, Protocol, Sequence

from langchain_core.embeddings import Embeddings

from ..core.config import Settings

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:  # pragma: no cover
    OpenAIEmbeddings = None

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except ImportError:  # pragma: no cover
    GoogleGenerativeAIEmbeddings = None


class EmbeddingProvider(Protocol):
    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        ...

    def embed_query(self, text: str) -> List[float]:
        ...


class LocalHashEmbeddingProvider:
    """Deterministic pseudo-embeddings when no API key is available."""

    def __init__(self, dimension: int = 256) -> None:
        self.dimension = dimension

    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        return [self._vectorize(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._vectorize(text)

    def _vectorize(self, text: str) -> List[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        seed = int.from_bytes(digest, "big")
        rng = random.Random(seed)
        return [rng.uniform(-1, 1) for _ in range(self.dimension)]


class LangChainEmbeddingProvider:
    """Adapts LangChain embedding models to the EmbeddingProvider protocol."""

    def __init__(self, embeddings: Embeddings) -> None:
        self.embeddings = embeddings

    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(list(texts))

    def embed_query(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)


def build_embeddings(settings: Settings) -> EmbeddingProvider:
    provider = (settings.embedding_provider or "auto").lower()

    if provider in ("auto", "openai"):
        if settings.openai_api_key and OpenAIEmbeddings is not None:
            return LangChainEmbeddingProvider(
                OpenAIEmbeddings(
                    model=settings.embedding_model,
                    api_key=settings.openai_api_key,
                )
            )
        if provider == "openai":
            return LocalHashEmbeddingProvider()

    if provider in ("auto", "gemini"):
        if settings.gemini_api_key and GoogleGenerativeAIEmbeddings is not None:
            return LangChainEmbeddingProvider(
                GoogleGenerativeAIEmbeddings(
                    model=settings.gemini_embedding_model,
                    google_api_key=settings.gemini_api_key,
                )
            )
        if provider == "gemini":
            return LocalHashEmbeddingProvider()

    return LocalHashEmbeddingProvider()


class EmbeddingService:
    """High-level helper that picks the appropriate provider."""

    def __init__(self, settings: Settings) -> None:
        self.provider: EmbeddingProvider = build_embeddings(settings)

    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        return self.provider.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.provider.embed_query(text)
