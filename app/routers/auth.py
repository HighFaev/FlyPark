from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import hash_password, login_user, logout_user, verify_password
from app.templating import render

router = APIRouter()


def _zaloguj(request: Request, db: Session, email: str, haslo: str, rola: str, szablon: str, cel: str):
    user = db.query(User).filter(User.email == email, User.role == rola).first()
    if not user or not verify_password(haslo, user.password_hash):
        return render(request, szablon, blad="Nieprawidłowy e-mail lub hasło.")
    login_user(request, user)
    return RedirectResponse(cel, status_code=303)


@router.get("/logowanie/klient")
def login_klient_form(request: Request):
    return render(request, "auth/login_klient.html")


@router.post("/logowanie/klient")
def login_klient(
    request: Request,
    email: str = Form(...),
    haslo: str = Form(...),
    db: Session = Depends(get_db),
):
    return _zaloguj(request, db, email, haslo, "client", "auth/login_klient.html", "/")


@router.get("/logowanie/pracownik")
def login_pracownik_form(request: Request):
    return render(request, "auth/login_pracownik.html")


@router.post("/logowanie/pracownik")
def login_pracownik(
    request: Request,
    email: str = Form(...),
    haslo: str = Form(...),
    db: Session = Depends(get_db),
):
    return _zaloguj(request, db, email, haslo, "employee", "auth/login_pracownik.html", "/panel")


@router.get("/rejestracja")
def rejestracja_form(request: Request):
    return render(request, "auth/rejestracja.html")


@router.post("/rejestracja")
def rejestracja(
    request: Request,
    imie: str = Form(...),
    nazwisko: str = Form(...),
    email: str = Form(...),
    telefon: str = Form(""),
    haslo: str = Form(...),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.email == email).first():
        return render(request, "auth/rejestracja.html", blad="Konto z tym e-mailem już istnieje.")
    user = User(
        email=email,
        password_hash=hash_password(haslo),
        role="client",
        imie=imie,
        nazwisko=nazwisko,
        telefon=telefon or None,
    )
    db.add(user)
    db.commit()
    login_user(request, user)
    return RedirectResponse("/", status_code=303)


@router.get("/wyloguj")
def wyloguj(request: Request):
    logout_user(request)
    return RedirectResponse("/", status_code=303)
