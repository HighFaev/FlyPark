from datetime import datetime, timedelta
from decimal import Decimal

from app.pricing import DEFAULT_CENNIK, oblicz_koszt

BAZA = datetime(2026, 6, 1, 8, 0)


def koszt(godziny=0, dni=0, typ="standard"):
    wyjazd = BAZA + timedelta(days=dni, hours=godziny)
    return oblicz_koszt(BAZA, wyjazd, DEFAULT_CENNIK, typ)


def test_dwie_godziny():
    assert koszt(godziny=2) == Decimal("15.00")


def test_osiem_godzin_liczone_godzinowo():
    assert koszt(godziny=8) == Decimal("45.00")


def test_dziewiec_godzin_to_pierwsza_doba():
    assert koszt(godziny=9) == Decimal("60.00")


def test_dwie_doby():
    assert koszt(dni=1, godziny=2) == Decimal("115.00")


def test_trzy_doby():
    assert koszt(dni=3) == Decimal("165.00")


def test_miejsce_zadaszone_jest_drozsze():
    assert koszt(godziny=2, typ="zadaszone") == Decimal("18.00")


def test_zerowy_czas_to_zero():
    assert koszt(godziny=0) == Decimal("0.00")


def test_wyjazd_przed_przyjazdem_to_zero():
    assert oblicz_koszt(BAZA, BAZA - timedelta(hours=3), DEFAULT_CENNIK) == Decimal("0.00")
