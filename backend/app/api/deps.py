"""Общие зависимости маршрутов API."""

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import get_current_user
from app.models import User

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
