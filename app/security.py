from fastapi import Depends, Request
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def login_user(request: Request, user: User) -> None:
    request.session["user_id"] = user.id
    request.session["role"] = user.role
    request.session["imie"] = user.imie or ""
    request.session["nazwisko"] = user.nazwisko or ""


def logout_user(request: Request) -> None:
    request.session.clear()


def current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.get(User, user_id)


class AuthRedirect(Exception):
    """Sygnalizuje brak uprawnień - obsługiwane przez przekierowanie na logowanie."""

    def __init__(self, location: str):
        self.location = location


def require_employee(user: User | None = Depends(current_user)) -> User:
    if user is None or user.role != "employee":
        raise AuthRedirect("/logowanie/pracownik")
    return user


def require_client(user: User | None = Depends(current_user)) -> User:
    if user is None or user.role != "client":
        raise AuthRedirect("/logowanie/klient")
    return user
