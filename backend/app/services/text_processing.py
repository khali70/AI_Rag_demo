from __future__ import annotations

from pathlib import Path

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
            return self._extract_pdf(file_path)

        raise TextExtractionError(f"Unsupported file type: {suffix}")

    @staticmethod
    def _extract_pdf(file_path: Path) -> str:
        reader = PdfReader(str(file_path))
        pages_text: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages_text.append(page_text.strip())
        return "\n\n".join(filter(None, pages_text))
