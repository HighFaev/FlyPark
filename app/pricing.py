from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from math import ceil

# Mnożnik dla miejsca zadaszonego (droższe niż standardowe).
MNOZNIK_ZADASZONE = Decimal("1.2")

DEFAULT_CENNIK = {
    "pierwsza_godzina": Decimal("10"),
    "kolejna_godzina": Decimal("5"),
    "pierwsza_doba": Decimal("60"),
    "doby_1_2": Decimal("55"),
    "doby_3_4": Decimal("50"),
    "kolejna_doba": Decimal("45"),
}


def _cena_za_dobe(numer_doby: int, cennik: dict) -> Decimal:
    if numer_doby == 1:
        return cennik["pierwsza_doba"]
    if numer_doby == 2:
        return cennik["doby_1_2"]
    if numer_doby in (3, 4):
        return cennik["doby_3_4"]
    return cennik["kolejna_doba"]


def oblicz_koszt(
    przyjazd: datetime,
    wyjazd: datetime,
    cennik: dict | None = None,
    typ_miejsca: str = "standard",
) -> Decimal:
    """Liczy koszt postoju na podstawie czasu i cennika.

    Do 9 godzin liczone godzinowo, powyżej - dobowo z malejącymi stawkami.
    """
    cennik = cennik or DEFAULT_CENNIK

    sekundy = (wyjazd - przyjazd).total_seconds()
    if sekundy <= 0:
        return Decimal("0.00")

    godziny = ceil(sekundy / 3600)

    if godziny < 9:
        koszt = cennik["pierwsza_godzina"] + (godziny - 1) * cennik["kolejna_godzina"]
    else:
        doby = ceil(godziny / 24)
        koszt = sum((_cena_za_dobe(i, cennik) for i in range(1, doby + 1)), Decimal("0"))

    if typ_miejsca == "zadaszone":
        koszt = koszt * MNOZNIK_ZADASZONE

    return Decimal(koszt).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def cennik_z_pozycji(pozycje) -> dict:
    """Zamienia listę obiektów PriceItem na słownik kod -> cena."""
    return {p.kod: Decimal(str(p.cena)) for p in pozycje}
