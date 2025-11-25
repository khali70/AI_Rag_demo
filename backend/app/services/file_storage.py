from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool


class FileStorageService:
    """Persist uploaded files to disk and return metadata."""

    def __init__(self, base_directory: str | Path) -> None:
        base_path = Path(base_directory).expanduser()
        base_path.mkdir(parents=True, exist_ok=True)
        self.base_directory = base_path.resolve()

    async def save_upload(self, upload: UploadFile) -> dict[str, Any]:
        safe_name = Path(upload.filename or "upload").name.replace(" ", "_")
        stored_name = f"{uuid4().hex}_{safe_name}"
        destination = self.base_directory / stored_name

        await upload.seek(0)
        size_bytes = await run_in_threadpool(self._copy_to_disk, upload, destination)

        return {
            "original_name": upload.filename or stored_name,
            "stored_name": stored_name,
            "content_type": upload.content_type or "application/octet-stream",
            "size_bytes": size_bytes,
            "storage_path": str(destination),
            "uploaded_at": datetime.utcnow(),
        }

    @staticmethod
    def _copy_to_disk(upload: UploadFile, destination: Path) -> int:
        upload.file.seek(0)
        with destination.open("wb") as out_file:
            shutil.copyfileobj(upload.file, out_file)
        return destination.stat().st_size
