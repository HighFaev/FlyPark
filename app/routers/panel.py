from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PriceItem, Reservation, User
from app.pricing import cennik_z_pozycji, oblicz_koszt
from app.routers.public import parse_dt
from app.security import require_employee
from app.templating import render

router = APIRouter(prefix="/panel")

TOTAL_MIEJSCA = 100


@router.get("")
def pulpit(request: Request, db: Session = Depends(get_db), user: User = Depends(require_employee)):
    teraz = datetime.utcnow()
    aktywne = db.query(Reservation).filter(Reservation.status == "aktywna")

    zajete = aktywne.filter(Reservation.data_przyjazdu <= teraz, Reservation.data_wyjazdu >= teraz).count()
    zarezerwowane = aktywne.filter(Reservation.data_przyjazdu > teraz).count()
    wolne = max(TOTAL_MIEJSCA - zajete - zarezerwowane, 0)
    zajetosc_proc = round(zajete / TOTAL_MIEJSCA * 100)

    najblizsze = (
        db.query(Reservation)
        .filter(Reservation.status == "aktywna", Reservation.data_wyjazdu >= teraz)
        .order_by(Reservation.data_wyjazdu.asc())
        .limit(10)
        .all()
    )

    return render(
        request,
        "panel/pulpit.html",
        active="pulpit",
        wolne=wolne,
        zarezerwowane=zarezerwowane,
        zajete=zajete,
        zajetosc_proc=zajetosc_proc,
        najblizsze=najblizsze,
    )


@router.get("/rezerwacje")
def rezerwacje(
    request: Request,
    q: str = "",
    oplacony: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(require_employee),
):
    zapytanie = db.query(Reservation)
    if q:
        zapytanie = zapytanie.filter(Reservation.nr_rej_pojazdu.ilike(f"%{q}%"))
    if oplacony == "tak":
        zapytanie = zapytanie.filter(Reservation.oplacony.is_(True))
    elif oplacony == "nie":
        zapytanie = zapytanie.filter(Reservation.oplacony.is_(False))

    lista = zapytanie.order_by(Reservation.data_przyjazdu.asc()).all()
    return render(
        request,
        "panel/rezerwacje.html",
        active="rezerwacje",
        rezerwacje=lista,
        q=q,
        oplacony=oplacony,
    )


@router.get("/rezerwacje/{rez_id}")
def szczegoly(
    request: Request,
    rez_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_employee),
):
    r = db.get(Reservation, rez_id)
    if not r:
        return RedirectResponse("/panel/rezerwacje", status_code=303)
    return render(request, "panel/szczegoly.html", active="rezerwacje", r=r)


@router.post("/rezerwacje/{rez_id}/skoryguj")
def skoryguj(
    request: Request,
    rez_id: int,
    data_przyjazdu: str = Form(...),
    data_wyjazdu: str = Form(...),
    nr_rej_pojazdu: str = Form(...),
    liczba_osob: int = Form(1),
    uwagi: str = Form(""),
    oplacony: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_employee),
):
    r = db.get(Reservation, rez_id)
    if not r:
        return RedirectResponse("/panel/rezerwacje", status_code=303)

    p, w = parse_dt(data_przyjazdu), parse_dt(data_wyjazdu)
    if p:
        r.data_przyjazdu = p
    if w:
        r.data_wyjazdu = w
    r.nr_rej_pojazdu = nr_rej_pojazdu
    r.liczba_osob = liczba_osob
    r.uwagi = uwagi or None
    r.oplacony = bool(oplacony)

    if r.data_wyjazdu > r.data_przyjazdu:
        cennik = cennik_z_pozycji(db.query(PriceItem).all())
        r.koszt = oblicz_koszt(r.data_przyjazdu, r.data_wyjazdu, cennik, r.typ_miejsca)

    db.commit()
    request.session["flash"] = "Zmiany zostały zapisane."
    return RedirectResponse(f"/panel/rezerwacje/{rez_id}", status_code=303)


@router.post("/rezerwacje/{rez_id}/anuluj")
def anuluj(
    request: Request,
    rez_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_employee),
):
    r = db.get(Reservation, rez_id)
    if r:
        r.status = "anulowana"
        db.commit()
        request.session["flash"] = "Postój został anulowany."
    return RedirectResponse(f"/panel/rezerwacje/{rez_id}", status_code=303)
