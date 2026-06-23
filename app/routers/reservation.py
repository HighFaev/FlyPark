import re
from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PriceItem, Reservation
from app.pricing import cennik_z_pozycji, oblicz_koszt
from app.routers.public import parse_dt
from app.templating import render

router = APIRouter(prefix="/rezerwacja")

PLATE_RE = re.compile(r"^[A-Za-z0-9 \-]{3,12}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _koszt(db: Session, dane: dict):
    p, w = parse_dt(dane.get("przyjazd")), parse_dt(dane.get("wyjazd"))
    if not (p and w and w > p):
        return None
    cennik = cennik_z_pozycji(db.query(PriceItem).all())
    return oblicz_koszt(p, w, cennik, dane.get("typ_miejsca", "standard"))


@router.get("")
def krok1(
    request: Request,
    przyjazd: str = "",
    wyjazd: str = "",
    typ_miejsca: str = "standard",
    db: Session = Depends(get_db),
):
    dane = request.session.get("rezerwacja", {})
    if przyjazd:
        dane["przyjazd"] = przyjazd
    if wyjazd:
        dane["wyjazd"] = wyjazd
    if typ_miejsca:
        dane["typ_miejsca"] = typ_miejsca
    request.session["rezerwacja"] = dane
    return render(request, "reservation/krok1.html", active="rezerwacja", dane=dane, koszt=_koszt(db, dane))


@router.post("")
def krok1_zapisz(
    request: Request,
    przyjazd: str = Form(...),
    wyjazd: str = Form(...),
    typ_miejsca: str = Form("standard"),
    db: Session = Depends(get_db),
):
    p, w = parse_dt(przyjazd), parse_dt(wyjazd)
    dane = request.session.get("rezerwacja", {})
    dane.update({"przyjazd": przyjazd, "wyjazd": wyjazd, "typ_miejsca": typ_miejsca})
    request.session["rezerwacja"] = dane

    blad = None
    if not (p and w):
        blad = "Podaj poprawną datę i godzinę przyjazdu oraz wyjazdu."
    elif p < datetime.now():
        blad = "Data przyjazdu nie może być w przeszłości."
    elif w <= p:
        blad = "Data wyjazdu musi być późniejsza niż data przyjazdu."

    if blad:
        return render(
            request,
            "reservation/krok1.html",
            active="rezerwacja",
            dane=dane,
            koszt=None,
            blad=blad,
        )
    return RedirectResponse("/rezerwacja/dane", status_code=303)


@router.get("/dane")
def krok2(request: Request):
    dane = request.session.get("rezerwacja", {})
    if not dane.get("przyjazd"):
        return RedirectResponse("/rezerwacja", status_code=303)
    return render(request, "reservation/krok2.html", active="rezerwacja", dane=dane)


@router.post("/dane")
def krok2_zapisz(
    request: Request,
    imie: str = Form(...),
    nazwisko: str = Form(...),
    telefon: str = Form(...),
    email: str = Form(...),
    nr_rej_pojazdu: str = Form(...),
    nr_lotu_powrotnego: str = Form(""),
    liczba_osob: int = Form(1),
    odbior_z_lotniska: str = Form(None),
):
    dane = request.session.get("rezerwacja", {})
    dane.update(
        {
            "imie": imie,
            "nazwisko": nazwisko,
            "telefon": telefon,
            "email": email,
            "nr_rej_pojazdu": nr_rej_pojazdu,
            "nr_lotu_powrotnego": nr_lotu_powrotnego,
            "liczba_osob": liczba_osob,
            "odbior_z_lotniska": bool(odbior_z_lotniska),
        }
    )
    request.session["rezerwacja"] = dane

    blad = None
    if not EMAIL_RE.match(email.strip()):
        blad = "Podaj poprawny adres e-mail."
    elif not PLATE_RE.match(nr_rej_pojazdu.strip()):
        blad = "Nr rejestracyjny powinien mieć od 3 do 12 znaków (litery, cyfry, spacje)."
    elif len(re.sub(r"\D", "", telefon)) < 7:
        blad = "Podaj poprawny numer telefonu (minimum 7 cyfr)."
    elif liczba_osob < 1 or liczba_osob > 9:
        blad = "Liczba osób musi być od 1 do 9."

    if blad:
        return render(request, "reservation/krok2.html", active="rezerwacja", dane=dane, blad=blad)

    return RedirectResponse("/rezerwacja/podsumowanie", status_code=303)


@router.get("/podsumowanie")
def krok3(request: Request, db: Session = Depends(get_db)):
    dane = request.session.get("rezerwacja", {})
    if not dane.get("imie"):
        return RedirectResponse("/rezerwacja", status_code=303)
    return render(request, "reservation/krok3.html", active="rezerwacja", dane=dane, koszt=_koszt(db, dane))


@router.post("/zatwierdz")
def zatwierdz(request: Request, forma_platnosci: str = Form(...), db: Session = Depends(get_db)):
    dane = request.session.get("rezerwacja", {})
    p, w = parse_dt(dane.get("przyjazd")), parse_dt(dane.get("wyjazd"))
    if not dane.get("imie") or not (p and w) or w <= p:
        return RedirectResponse("/rezerwacja", status_code=303)

    koszt = _koszt(db, dane)
    rezerwacja = Reservation(
        imie=dane["imie"],
        nazwisko=dane["nazwisko"],
        telefon=dane["telefon"],
        email=dane["email"],
        nr_rej_pojazdu=dane["nr_rej_pojazdu"],
        nr_lotu_powrotnego=dane.get("nr_lotu_powrotnego") or None,
        liczba_osob=dane.get("liczba_osob", 1),
        odbior_z_lotniska=dane.get("odbior_z_lotniska", False),
        data_przyjazdu=p,
        data_wyjazdu=w,
        typ_miejsca=dane.get("typ_miejsca", "standard"),
        koszt=koszt,
        oplacony=forma_platnosci != "szlaban",
        forma_platnosci=forma_platnosci,
        status="aktywna",
        user_id=request.session.get("user_id"),
    )
    db.add(rezerwacja)
    db.commit()

    request.session.pop("rezerwacja", None)
    request.session["flash"] = f"Rezerwacja potwierdzona. Numer: {rezerwacja.id}."
    return RedirectResponse("/", status_code=303)
