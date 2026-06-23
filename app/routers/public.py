from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PriceItem
from app.pricing import cennik_z_pozycji, oblicz_koszt
from app.templating import render

router = APIRouter()

DT_FORMAT = "%Y-%m-%dT%H:%M"


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, DT_FORMAT)
    except ValueError:
        return None


@router.get("/")
def home(request: Request):
    return render(request, "public/home.html", active="home")


@router.get("/cennik")
def cennik(request: Request, db: Session = Depends(get_db)):
    pozycje = db.query(PriceItem).all()
    return render(request, "public/cennik.html", active="cennik", pozycje=pozycje, koszt=None)


@router.post("/cennik/oblicz")
def cennik_oblicz(
    request: Request,
    przyjazd: str = Form(...),
    wyjazd: str = Form(...),
    typ_miejsca: str = Form("standard"),
    db: Session = Depends(get_db),
):
    pozycje = db.query(PriceItem).all()
    p, w = parse_dt(przyjazd), parse_dt(wyjazd)
    koszt = None
    if p and w and w > p:
        koszt = oblicz_koszt(p, w, cennik_z_pozycji(pozycje), typ_miejsca)
    return render(
        request,
        "public/cennik.html",
        active="cennik",
        pozycje=pozycje,
        koszt=koszt,
        przyjazd=przyjazd,
        wyjazd=wyjazd,
        typ_miejsca=typ_miejsca,
    )


@router.get("/kontakt")
def kontakt(request: Request):
    return render(request, "public/kontakt.html", active="kontakt")


@router.post("/kontakt")
def kontakt_wyslij(
    request: Request,
    imie: str = Form(...),
    nazwisko: str = Form(...),
    email: str = Form(...),
    wiadomosc: str = Form(...),
    zgoda: str = Form(None),
):
    request.session["flash"] = "Dziękujemy, wiadomość została wysłana."
    return RedirectResponse("/kontakt", status_code=303)
