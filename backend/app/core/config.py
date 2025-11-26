from functools import lru_cache
from json import loads
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = Field(default="NixAI Backend", alias="APP_NAME")
    env: str = Field(default="development", alias="ENV")
    backend_cors_origins: List[str] | str = Field(default="*", alias="BACKEND_CORS_ORIGINS")

    database_url: str = Field(
        default="sqlite:///./storage/nixai.db",
        description="SQLAlchemy-compatible connection URL.",
        alias="DATABASE_URL",
    )
    chroma_persist_dir: str = Field(default="./storage/chroma", alias="CHROMA_PERSIST_DIR")
    chroma_server_host: Optional[str] = Field(
        default=None,
        description="If provided, the backend will use Chroma's HTTP client instead of the embedded persistent client.",
        alias="CHROMA_SERVER_HOST",
    )
    chroma_server_port: int = Field(default=8000, alias="CHROMA_SERVER_PORT")
    chroma_server_ssl: bool = Field(default=False, alias="CHROMA_SERVER_SSL")
    uploads_dir: str = Field(default="./storage/uploads", alias="UPLOADS_DIR")
    default_user_id: str = Field(default="demo-user", alias="DEFAULT_USER_ID")

    text_splitter_chunk_size: int = Field(default=800, alias="TEXT_SPLITTER_CHUNK_SIZE")
    text_splitter_chunk_overlap: int = Field(default=200, alias="TEXT_SPLITTER_CHUNK_OVERLAP")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    chat_model: str = Field(default="gpt-4o-mini", description="Default OpenAI chat model.", alias="CHAT_MODEL")
    gemini_chat_model: str = Field(
        description="Default Gemini chat model.",
        alias="GEMINI_CHAT_MODEL",
    )

    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")

    jwt_secret_key: str = Field(default="change-me", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, list):
            return [origin.strip() for origin in value if isinstance(origin, str) and origin.strip()]

        text = (value or "").strip()
        if not text or text == "*":
            return ["*"]

        if text.startswith("["):
            try:
                data = loads(text)
                if isinstance(data, list):
                    return [str(origin).strip() for origin in data if str(origin).strip()]
            except Exception:
                # Fall back to comma-separated parsing below
                pass

        parts = [origin.strip() for origin in text.split(",") if origin.strip()]
        return parts or ["*"]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings to avoid re-parsing .env."""
    return Settings()
