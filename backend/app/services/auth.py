from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def decode_token(token: str) -> Optional[str]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
    subject: str | None = payload.get("sub")
    return subject


def _parse_refresh_token(token: str) -> tuple[str, str] | None:
    try:
        token_id, secret = token.split(".", 1)
    except ValueError:
        return None
    return token_id, secret


def create_refresh_token() -> str:
    token_id = uuid4().hex
    secret = uuid4().hex
    return f"{token_id}.{secret}"


def store_refresh_token(db: Session, user: User, token: str) -> None:
    settings = get_settings()
    parsed = _parse_refresh_token(token)
    if not parsed:
        return
    token_id, _ = parsed
    user.refresher_id = token_id
    user.refresh_token_hash = pwd_context.hash(token)
    user.refresh_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.refresh_token_expire_minutes)
    db.add(user)
    db.commit()
    db.refresh(user)


def clear_refresh_token(db: Session, user: User) -> None:
    user.refresher_id = None
    user.refresh_token_hash = None
    user.refresh_token_expires_at = None
    db.add(user)
    db.commit()


def get_user_by_refresh_token(db: Session, token: str) -> Optional[User]:
    parsed = _parse_refresh_token(token)
    if not parsed:
        return None
    token_id, _ = parsed
    user = db.query(User).filter(User.refresher_id == token_id).first()
    if not user or not user.refresh_token_hash or not user.refresh_token_expires_at:
        return None

    if datetime.now(timezone.utc) > user.refresh_token_expires_at:
        clear_refresh_token(db, user)
        return None

    if not pwd_context.verify(token, user.refresh_token_hash):
        return None

    return user
