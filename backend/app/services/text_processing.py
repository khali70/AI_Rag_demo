from __future__ import annotations

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
import tiktoken 
from pypdf import PdfReader


class TextExtractionError(Exception):
    """Raised when text cannot be extracted from an upload."""


class TextExtractionService:
    """Extract raw text content from supported document formats."""

    SUPPORTED_EXTENSIONS = {".txt", ".pdf"}

    def extract_text(self, file_path: Path, content_type: str | None = None) -> str:
        suffix = file_path.suffix.lower()
        if suffix not in self.SUPPORTED_EXTENSIONS:
            raise TextExtractionError(f"Unsupported file type: {suffix}")

        if suffix == ".txt":
            return file_path.read_text(encoding="utf-8", errors="ignore")
        if suffix == ".pdf":
            res = self._extract_pdf(file_path)
            print(len(tiktoken.get_encoding("cl100k_base").encode(res)))
            return res

        raise TextExtractionError(f"Unsupported file type: {suffix}")

    @staticmethod
    def _extract_pdf(file_path: Path) -> str:
        # Prefer LangChain's PDF loader for more resilient extraction (handles layout quirks, encodings, etc.).
        try:
            docs = PyPDFLoader(str(file_path)).load()
            if docs:
                return "\n\n".join(doc.page_content.strip() for doc in docs if doc.page_content)
        except Exception as exc:
            print(f"LangChain PDF extraction failed for {file_path}: {exc}")

        reader = PdfReader(str(file_path))
        pages_text: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages_text.append(page_text.strip())
        return "\n\n".join(filter(None, pages_text))
