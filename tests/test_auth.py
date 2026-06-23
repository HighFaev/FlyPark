from app.models import User


def test_rejestracja_tworzy_konto(client, db_session):
    resp = client.post(
        "/rejestracja",
        data={
            "imie": "Test",
            "nazwisko": "Testowy",
            "email": "nowy@poczta.pl",
            "telefon": "+48 111 222 333",
            "haslo": "tajne123",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert db_session.query(User).filter(User.email == "nowy@poczta.pl").count() == 1


def test_rejestracja_odrzuca_duplikat(client):
    resp = client.post(
        "/rejestracja",
        data={"imie": "A", "nazwisko": "B", "email": "klient@flypark.pl", "haslo": "x"},
    )
    assert "już istnieje" in resp.text


def test_logowanie_pracownika(client):
    resp = client.post(
        "/logowanie/pracownik",
        data={"email": "pracownik@flypark.pl", "haslo": "pracownik123"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "/panel"


def test_bledne_haslo(client):
    resp = client.post(
        "/logowanie/pracownik",
        data={"email": "pracownik@flypark.pl", "haslo": "zle"},
    )
    assert "Nieprawidłowy" in resp.text


def test_panel_niedostepny_dla_anonima(client):
    resp = client.get("/panel", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/logowanie/pracownik"


def test_panel_niedostepny_dla_klienta(client):
    client.post(
        "/logowanie/klient",
        data={"email": "klient@flypark.pl", "haslo": "klient123"},
        follow_redirects=False,
    )
    resp = client.get("/panel", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/logowanie/pracownik"
