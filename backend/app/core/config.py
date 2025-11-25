from functools import lru_cache
from json import loads
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = Field(default="NixAI Backend")
    env: str = Field(default="development")
    backend_cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    database_url: str = Field(
        default="sqlite:///./storage/nixai.db",
        description="SQLAlchemy-compatible connection URL.",
    )
    chroma_persist_dir: str = Field(default="./storage/chroma")
    chroma_server_host: Optional[str] = Field(
        default=None,
        description="If provided, the backend will use Chroma's HTTP client instead of the embedded persistent client.",
    )
    chroma_server_port: int = Field(default=8000)
    chroma_server_ssl: bool = Field(default=False)
    uploads_dir: str = Field(default="./storage/uploads")
    default_user_id: str = Field(default="demo-user")

    text_splitter_chunk_size: int = Field(default=800)
    text_splitter_chunk_overlap: int = Field(default=200)
    embedding_model: str = Field(default="text-embedding-3-small")
    chat_model: str = Field(default="gpt-4o-mini", description="Default OpenAI chat model.")
    gemini_chat_model: str = Field(default="gemini-1.5-flash", description="Default Gemini chat model.")

    openai_api_key: Optional[str] = Field(default=None)
    gemini_api_key: Optional[str] = Field(default=None)

    jwt_secret_key: str = Field(default="change-me")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, str):
            text = value.strip()
            if text.startswith("["):
                try:
                    data = loads(text)
                    if isinstance(data, list):
                        return [str(origin).strip() for origin in data if str(origin).strip()]
                except Exception:
                    pass
            return [origin.strip() for origin in text.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Return cached settings to avoid re-parsing .env."""
    return Settings()
