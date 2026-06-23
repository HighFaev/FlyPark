# FlyPark - System Zarządzania Parkingiem Lotniskowym

## Skład zespołu
- **Arseni Fayeu** – Team Leader
- **Mateusz Bosak** – Członek zespołu
- **Adriana Waszeciak** – Członek zespołu

## Temat projektu
Tematem projektu jest stworzenie responsywnej aplikacji webowej służącej do kompleksowego zarządzania prywatnymi parkingami zlokalizowanymi w sąsiedztwie lotnisk. System jest skierowany zarówno do właścicieli i pracowników parkingów, jak i do klientów korzystających z usług postoju.

## Wizja systemu
FlyPark ma na celu zrewolucjonizowanie sposobu prowadzenia ewidencji na małych parkingach poprzez zastąpienie metod tradycyjnych (zeszyty, arkusze Excel) nowoczesnym, zautomatyzowanym rozwiązaniem cyfrowym. 

Główne założenia systemu to:
- **Automatyzacja i oszczędność czasu:** Usprawnienie procesu rezerwacji online oraz automatyczne naliczanie opłat skraca czas obsługi klienta.
- **Optymalizacja zasobów:** Precyzyjny podgląd zajętości parkingu w czasie rzeczywistym pozwala na maksymalizację zysków i unikanie błędów w planowaniu.
- **Uporządkowany transport:** Przejrzysty harmonogram transferów na i z lotniska zapewnia terminowość oraz wyższy standard obsługi klienta.
- **Bezpieczeństwo danych:** Gromadzenie historii pojazdów i wpłat w jednym miejscu eliminuje ryzyko utraty informacji i ułatwia nadzór nad biznesem.

Aplikacja wykorzystuje powszechny dostęp do smartfonów, umożliwiając klientom błyskawiczną rezerwację, a pracownikom efektywne zarządzanie placówką z dowolnego urządzenia.

## Kanban's table
https://github.com/users/HighFaev/projects/3

## Opis aplikacji
Aplikacja webowa parkingu przy lotnisku. Klient rezerwuje miejsce online (wybór terminu, dane, podsumowanie i płatność), a pracownik zarządza rezerwacjami w panelu.

Projekt zaliczeniowy. Płatność jest tylko demonstracyjna (okno mock) - nie jest realizowana żadna prawdziwa transakcja.

## Stos technologiczny

- FastAPI + szablony Jinja2 (renderowanie po stronie serwera)
- Bootstrap 5 (CSS z CDN)
- PostgreSQL + SQLAlchemy
- Sesja przechowywana w podpisanym ciasteczku
- Testy: pytest

## Uruchomienie (Docker)

Wymagania: zainstalowany Docker. Na Windows/Mac przed uruchomieniem musi **działać Docker Desktop** (ikona wieloryba w zasobniku). Jeśli aplikacja nie jest uruchomiona, `docker compose` zgłosi błąd połączenia z demonem.

```bash
docker compose up --build
```

Aplikacja: http://localhost:8000

Przy pierwszym starcie baza jest tworzona i wypełniana danymi przykładowymi.

Przydatne komendy:

```bash
docker compose up --build -d     # uruchomienie w tle
docker compose ps                # status kontenerów
docker compose logs -f web       # podgląd logów aplikacji
docker compose down              # zatrzymanie (dane bazy zostają w wolumenie pgdata)
docker compose down -v           # zatrzymanie i usunięcie bazy danych
```

### Rozwiązywanie problemów

- Błąd `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`
  (lub `Cannot connect to the Docker daemon`) oznacza, że Docker Desktop nie jest uruchomiony.
  Uruchom Docker Desktop, poczekaj aż wystartuje, a następnie ponów `docker compose up --build`.
- Jeśli port 8000 jest zajęty, zmień mapowanie portu w `docker-compose.yml` (np. `"8001:8000"`).

## Konta demonstracyjne

| Rola      | E-mail                | Hasło         |
|-----------|-----------------------|---------------|
| Pracownik | pracownik@flypark.pl  | pracownik123  |
| Klient    | klient@flypark.pl     | klient123     |

## Funkcje

Strona publiczna:
- Strona główna z wyszukiwarką terminu
- Cennik z kalkulatorem kosztów
- Formularz kontaktowy
- Rezerwacja w 3 krokach (termin -> dane -> podsumowanie i płatność)
- Logowanie/rejestracja klienta, logowanie pracownika

Panel pracownika:
- Pulpit z zajętością parkingu i najbliższymi wyjazdami
- Lista rezerwacji z wyszukiwaniem i filtrowaniem
- Szczegóły rezerwacji z edycją danych i anulowaniem postoju

## Uruchomienie lokalne (bez Dockera)

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
set DATABASE_URL=sqlite:///./flypark.db
uvicorn app.main:app --reload
```

## Testy

```bash
pip install -r requirements.txt
pytest
```

Testy używają bazy SQLite, więc nie wymagają działającego PostgreSQL.

## Struktura

```
app/
  main.py            # aplikacja FastAPI, sesja, routery, start
  config.py          # konfiguracja z zmiennych środowiskowych
  database.py        # silnik bazy i sesje SQLAlchemy
  models.py          # User, Reservation, PriceItem
  pricing.py         # wyliczanie kosztu postoju
  security.py        # hasła i kontrola dostępu
  seed.py            # dane startowe
  routers/           # public, reservation, auth, panel
  templates/         # szablony Jinja2
  static/            # CSS
tests/               # testy pytest
```
