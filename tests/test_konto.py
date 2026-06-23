def test_konto_niedostepne_dla_anonima(client):
    resp = client.get("/konto", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/logowanie/klient"


def test_konto_niedostepne_dla_pracownika(employee_client):
    resp = employee_client.get("/konto", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/logowanie/klient"


def test_logowanie_klienta_przekierowuje_na_konto(client):
    resp = client.post(
        "/logowanie/klient",
        data={"email": "klient@flypark.pl", "haslo": "klient123"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "/konto"


def test_konto_pokazuje_rezerwacje_klienta(client_logged):
    resp = client_logged.get("/konto")
    assert resp.status_code == 200
    assert "Panel klienta" in resp.text
    assert "Aktywne rezerwacje" in resp.text
    assert "Historia parkingu" in resp.text
    assert "KR 77777" in resp.text


def test_konto_rozdziela_aktywne_i_historie(client_logged):
    resp = client_logged.get("/konto")
    assert "Zakończona" in resp.text
    assert "Anulowana" in resp.text


def test_nowa_rezerwacja_klienta_trafia_na_konto(client_logged):
    client_logged.post(
        "/rezerwacja",
        data={"przyjazd": "2030-07-01T08:00", "wyjazd": "2030-07-03T10:00", "typ_miejsca": "standard"},
    )
    client_logged.post(
        "/rezerwacja/dane",
        data={
            "imie": "Anna",
            "nazwisko": "Nowak",
            "telefon": "+48 500 600 700",
            "email": "klient@flypark.pl",
            "nr_rej_pojazdu": "KR 88888",
        },
    )
    client_logged.post("/rezerwacja/zatwierdz", data={"forma_platnosci": "karta"}, follow_redirects=False)

    resp = client_logged.get("/konto")
    assert "KR 88888" in resp.text
