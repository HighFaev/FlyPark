from app.models import Reservation


def test_pelny_proces_rezerwacji(client, db_session):
    r1 = client.post(
        "/rezerwacja",
        data={"przyjazd": "2026-07-01T08:00", "wyjazd": "2026-07-03T10:00", "typ_miejsca": "standard"},
        follow_redirects=False,
    )
    assert r1.status_code == 303
    assert r1.headers["location"] == "/rezerwacja/dane"

    r2 = client.post(
        "/rezerwacja/dane",
        data={
            "imie": "Jan",
            "nazwisko": "Testowy",
            "telefon": "+48 600 700 800",
            "email": "jan@poczta.pl",
            "nr_rej_pojazdu": "KR 00001",
            "liczba_osob": 2,
            "odbior_z_lotniska": "on",
        },
        follow_redirects=False,
    )
    assert r2.status_code == 303

    r3 = client.post(
        "/rezerwacja/zatwierdz",
        data={"forma_platnosci": "karta"},
        follow_redirects=False,
    )
    assert r3.status_code == 303

    rez = db_session.query(Reservation).filter(Reservation.nr_rej_pojazdu == "KR 00001").first()
    assert rez is not None
    assert rez.imie == "Jan"
    assert rez.oplacony is True
    assert float(rez.koszt) > 0


def test_platnosc_przy_szlabanie_nie_jest_oplacona(client, db_session):
    client.post(
        "/rezerwacja",
        data={"przyjazd": "2026-07-01T08:00", "wyjazd": "2026-07-02T08:00", "typ_miejsca": "standard"},
    )
    client.post(
        "/rezerwacja/dane",
        data={
            "imie": "Ewa",
            "nazwisko": "Test",
            "telefon": "123",
            "email": "ewa@poczta.pl",
            "nr_rej_pojazdu": "KR 22222",
        },
    )
    client.post("/rezerwacja/zatwierdz", data={"forma_platnosci": "szlaban"}, follow_redirects=False)

    rez = db_session.query(Reservation).filter(Reservation.nr_rej_pojazdu == "KR 22222").first()
    assert rez is not None
    assert rez.oplacony is False


def test_bledne_daty_pokazuja_komunikat(client):
    resp = client.post(
        "/rezerwacja",
        data={"przyjazd": "2026-07-05T08:00", "wyjazd": "2026-07-01T08:00", "typ_miejsca": "standard"},
    )
    assert "późniejsza" in resp.text
