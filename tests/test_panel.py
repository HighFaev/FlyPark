from app.models import Reservation


def _pierwsza_rezerwacja(db_session):
    return db_session.query(Reservation).order_by(Reservation.id.asc()).first()


def test_lista_rezerwacji(employee_client):
    resp = employee_client.get("/panel/rezerwacje")
    assert resp.status_code == 200
    assert "KR 12345" in resp.text


def test_wyszukiwanie_po_nr_rej(employee_client):
    resp = employee_client.get("/panel/rezerwacje", params={"q": "WA 99887"})
    assert "WA 99887" in resp.text
    assert "KR 12345" not in resp.text


def test_filtr_oplacone(employee_client, db_session):
    resp = employee_client.get("/panel/rezerwacje", params={"oplacony": "nie"})
    assert resp.status_code == 200


def test_szczegoly_rezerwacji(employee_client, db_session):
    rez = _pierwsza_rezerwacja(db_session)
    resp = employee_client.get(f"/panel/rezerwacje/{rez.id}")
    assert resp.status_code == 200
    assert rez.nr_rej_pojazdu in resp.text


def test_skoryguj_zapisuje_zmiany(employee_client, db_session):
    rez = _pierwsza_rezerwacja(db_session)
    resp = employee_client.post(
        f"/panel/rezerwacje/{rez.id}/skoryguj",
        data={
            "data_przyjazdu": "2026-08-01T08:00",
            "data_wyjazdu": "2026-08-02T08:00",
            "nr_rej_pojazdu": "ZM 00000",
            "liczba_osob": 3,
            "uwagi": "Test uwagi",
            "oplacony": "on",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    db_session.expire_all()
    odswiezona = db_session.get(Reservation, rez.id)
    assert odswiezona.nr_rej_pojazdu == "ZM 00000"
    assert odswiezona.uwagi == "Test uwagi"
    assert odswiezona.oplacony is True


def test_anulowanie_postoju(employee_client, db_session):
    rez = _pierwsza_rezerwacja(db_session)
    resp = employee_client.post(f"/panel/rezerwacje/{rez.id}/anuluj", follow_redirects=False)
    assert resp.status_code == 303
    db_session.expire_all()
    assert db_session.get(Reservation, rez.id).status == "anulowana"


def test_anonim_nie_widzi_listy(client):
    resp = client.get("/panel/rezerwacje", follow_redirects=False)
    assert resp.status_code == 303
