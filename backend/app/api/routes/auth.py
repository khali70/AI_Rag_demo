from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ...core.config import get_settings
from ...db.deps import get_db
from ...models.user import User
from ...schemas import RefreshRequest, Token, UserCreate, UserLogin, UserRead
from ...services.auth import (
    authenticate_user,
    clear_refresh_token,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_user_by_email,
    get_user_by_refresh_token,
    hash_password,
    store_refresh_token,
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    subject = decode_token(token)
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials.")

    user = db.get(User, subject)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    return user


def get_current_user_id(current_user: User = Depends(get_current_user)) -> str:
    return current_user.id

router = APIRouter()



@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    settings = get_settings()
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token()
    store_refresh_token(db, user, refresh_token)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        refresh_expires_in=settings.refresh_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=Token)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)) -> Token:
    user = get_user_by_refresh_token(db, payload.refresh_token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

    settings = get_settings()
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token()
    store_refresh_token(db, user, refresh_token)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        refresh_expires_in=settings.refresh_token_expire_minutes * 60,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> None:
    clear_refresh_token(db, current_user)


