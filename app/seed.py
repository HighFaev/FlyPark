from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import PriceItem, Reservation, User
from app.pricing import cennik_z_pozycji, oblicz_koszt
from app.security import hash_password

CENNIK_START = [
    ("pierwsza_godzina", "Pierwsza godzina", 10),
    ("kolejna_godzina", "Każda kolejna rozpoczęta godzina", 5),
    ("pierwsza_doba", "Pierwsza doba (powyżej 9 godzin)", 60),
    ("doby_1_2", "1-2 rozpoczęte doby", 55),
    ("doby_3_4", "3-4 rozpoczęte doby", 50),
    ("kolejna_doba", "Każda następna doba", 45),
]


def seed(db: Session) -> None:
    if db.query(PriceItem).count() == 0:
        for kod, nazwa, cena in CENNIK_START:
            db.add(PriceItem(kod=kod, nazwa=nazwa, cena=cena))
        db.commit()

    if db.query(User).count() == 0:
        db.add(
            User(
                email="pracownik@flypark.pl",
                password_hash=hash_password("pracownik123"),
                role="employee",
                imie="Jan",
                nazwisko="Kowalski",
                telefon="+48 123 123 123",
            )
        )
        db.add(
            User(
                email="klient@flypark.pl",
                password_hash=hash_password("klient123"),
                role="client",
                imie="Anna",
                nazwisko="Nowak",
                telefon="+48 500 600 700",
            )
        )
        db.commit()

    if db.query(Reservation).count() == 0:
        cennik = cennik_z_pozycji(db.query(PriceItem).all())
        teraz = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        przyklady = [
            ("KR 12345", "Adam", "Wiśniewski", 3, "standard", True, True),
            ("KR 54321", "Ewa", "Lewandowska", 1, "zadaszone", False, False),
            ("WA 99887", "Piotr", "Zieliński", 2, "standard", True, False),
            ("GD 11223", "Maria", "Wójcik", 4, "zadaszone", True, True),
            ("PO 44556", "Tomasz", "Kamiński", 1, "standard", False, True),
        ]
        for i, (rej, imie, nazwisko, dni, typ, oplacony, transfer) in enumerate(przyklady):
            przyjazd = teraz + timedelta(days=i, hours=8)
            wyjazd = przyjazd + timedelta(days=dni, hours=2)
            koszt = oblicz_koszt(przyjazd, wyjazd, cennik, typ)
            db.add(
                Reservation(
                    imie=imie,
                    nazwisko=nazwisko,
                    telefon="+48 600 700 800",
                    email=f"{nazwisko.lower()}@poczta.pl",
                    nr_rej_pojazdu=rej,
                    nr_lotu_powrotnego="LO123",
                    liczba_osob=dni,
                    odbior_z_lotniska=transfer,
                    data_przyjazdu=przyjazd,
                    data_wyjazdu=wyjazd,
                    typ_miejsca=typ,
                    koszt=koszt,
                    oplacony=oplacony,
                    forma_platnosci="karta" if oplacony else None,
                    status="aktywna",
                )
            )
        db.commit()
