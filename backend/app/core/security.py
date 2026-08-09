"""Хэширование паролей и проверка JWT-токенов."""

from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session

from app.core.config import settings
from app.core.db import get_session
from app.models import User

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


def hash_password(password: str) -> str:
    """Возвращает безопасный хэш пароля."""
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Сверяет пароль с сохранённым хэшем."""
    return pwd_context.verify(password, password_hash)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    """Создаёт подписанный токен доступа для пользователя."""
    expires_at = datetime.now(UTC) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": subject, "exp": expires_at}, settings.secret_key, algorithm=ALGORITHM
    )


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> User:
    """Извлекает текущего активного пользователя по Bearer JWT."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_error
    except JWTError as exc:
        raise credentials_error from exc
    user = session.get(User, int(user_id))
    if not user or not user.is_active:
        raise credentials_error
    return user
