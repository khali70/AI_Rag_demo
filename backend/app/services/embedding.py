from __future__ import annotations

import hashlib
import random
from typing import List, Protocol, Sequence

from ..core.config import Settings

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None


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


class OpenAIEmbeddingProvider:
    """Wraps the OpenAI embeddings API."""

    def __init__(self, api_key: str, model: str) -> None:
        if OpenAI is None:  # pragma: no cover
            raise RuntimeError("openai package is not available")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        response = self.client.embeddings.create(model=self.model, input=list(texts))
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]


class EmbeddingService:
    """High-level helper that picks the appropriate provider."""

    def __init__(self, settings: Settings) -> None:
        if settings.openai_api_key:
            self.provider: EmbeddingProvider = OpenAIEmbeddingProvider(
                api_key=settings.openai_api_key,
                model=settings.embedding_model,
            )
        else:
            self.provider = LocalHashEmbeddingProvider()

    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        return self.provider.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.provider.embed_query(text)
