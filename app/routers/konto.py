from datetime import datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Reservation, User
from app.security import require_client
from app.templating import render

router = APIRouter(prefix="/konto")


@router.get("")
def konto(request: Request, db: Session = Depends(get_db), user: User = Depends(require_client)):
    teraz = datetime.utcnow()

    aktywne = (
        db.query(Reservation)
        .filter(
            Reservation.user_id == user.id,
            Reservation.status == "aktywna",
            Reservation.data_wyjazdu >= teraz,
        )
        .order_by(Reservation.data_przyjazdu.asc())
        .all()
    )

    historia = (
        db.query(Reservation)
        .filter(
            Reservation.user_id == user.id,
            or_(Reservation.status == "anulowana", Reservation.data_wyjazdu < teraz),
        )
        .order_by(Reservation.data_wyjazdu.desc())
        .all()
    )

    return render(
        request,
        "konto/panel.html",
        active="konto",
        user=user,
        aktywne=aktywne,
        historia=historia,
    )
