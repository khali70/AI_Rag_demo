from collections.abc import Generator

from sqlalchemy.orm import Session

from .session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Provide a SQLAlchemy session dependency for FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
