# Nutrition App

Aplikacja żywieniowa — monorepo z backendem (FastAPI + PostgreSQL) i frontendem (React + Vite).

---

## Uruchomienie w Dockerze

Wymagania: Docker + Docker Compose.

Jedno polecenie stawia cały stack (front + backend + Postgres), nakłada migracje
i wypełnia bazę danymi (`seed.py`, idempotentnie):

```bash
docker compose up --build
```

- Aplikacja: <http://localhost:5173/>
- Swagger UI: <http://localhost:8000/docs>

Frontend jest budowany produkcyjnie i serwowany przez nginx, który reverse-proxuje
`/api/*` do backendu (ten sam mechanizm co proxy Vite w dev — front działa bez zmian,
a cookie sesji jest same-origin).

Dane logowania z seeda: admin `admin@nutrition.local` / `Admin123!`,
użytkownicy `*@example.com` / `Password1!`.

Reset bazy (usuwa wolumen z danymi i seeduje od nowa):

```bash
docker compose down -v
```

Konfiguracja jest opcjonalna — wszystkie zmienne mają wartości domyślne. Aby zmienić
hasło/nazwę bazy albo podać dane SMTP, skopiuj szablon do `.env` obok `docker-compose.yml`:

```bash
cp .env.docker.example .env
```

Zmienne bazy: `migrate.py` czyta `DB_PASS`, a aplikacja i `seed.py` czytają `DB_PASSWORD`.
Compose ustawia obie na tę samą wartość (`${DB_PASS}`), więc nie trzeba zmieniać kodu.
Entrypoint backendu czeka aż baza przyjmie połączenia, nakłada migracje
(`RUN_MIGRATIONS=true`), seeduje (`SEED_DB=true`) i startuje uvicorn na `0.0.0.0:8000`.

Poczta (2FA / reset hasła): bez `SMTP_USERNAME` / `SMTP_PASSWORD` rejestracja działa,
ale mail z kodem się nie wyśle.

---

## Uruchomienie lokalne (bez Dockera)

### 1. Backend

Wymagania: Python 3.10+, pip, działająca instancja PostgreSQL.

```bash
cd backend

# środowisko wirtualne
python -m venv .venv
.venv\Scripts\activate           # Windows
source .venv/bin/activate        # Linux / macOS

# zależności
pip install -r requirements.txt

# konfiguracja .env (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT, SMTP_*)
cp .env.example .env

# migracje
python migrate.py

# (opcjonalnie) dane przykładowe — patrz sekcja Seed
python seed.py

# start serwera (jawnie IPv4 — patrz notka o sieci lokalnej poniżej)
uvicorn app.main:app --reload --host 127.0.0.1
```

- API: <http://localhost:8000/>
- Swagger UI: <http://localhost:8000/docs>

Sieć lokalna na Windows (localhost = IPv4 vs IPv6): `localhost` rozwiązuje się i na
`127.0.0.1` (IPv4), i na `::1` (IPv6), a różne programy próbują ich w różnej kolejności.
Jeśli usługa słucha tylko na jednej rodzinie, połączenie w drugą jest na Windows cicho
upuszczane i klient czeka 0,25–2 s na timeout. Dlatego cały stack lokalny jest spięty
po IPv4: backend `uvicorn --host 127.0.0.1`, Vite `server.host: '127.0.0.1'` + proxy
→ `http://127.0.0.1:8000`, baza w `.env` `DB_HOST=127.0.0.1`.

### 2. Frontend

Wymagania: Node 18+, npm.

```bash
cd frontend
npm install
npm run dev
```

- Aplikacja: <http://localhost:5173/>

Frontend w trybie dev używa proxy Vite: wszystkie wywołania API idą pod prefiksem `/api`,
a Vite przekierowuje tylko `/api/*` → `http://127.0.0.1:8000` (zdejmując prefiks `/api`
przed przekazaniem do backendu). Dzięki temu trasy SPA (`/recipes`, `/products`, `/meals`,
`/leaderboard`, …) nie kolidują z proxy i odświeżenie dowolnej podstrony serwuje aplikację
zamiast przekierowywać na backend. Cookie sesji (httpOnly, SameSite=Lax) działa same-origin.
Backend ma dodatkowo `CORSMiddleware` z `allow_credentials=True` dla `http://localhost:5173`.

---

## Seed (dane przykładowe)

Skrypt `backend/seed.py` wstawia gotowy zestaw użytkowników, produktów i przepisów.
Jest idempotentny — pomija rekordy już istniejące.

```bash
cd backend
python seed.py                          # admin z domyślnym mailem
python seed.py --admin-email mail@x.pl  # własny e-mail admina
```

Co tworzy:

| Typ | Ilość | Szczegóły |
|---|---|---|
| Admin | 1 | `admin@nutrition.local` / `Admin123!` (rola `ADMIN`) |
| Użytkownicy | 5 | `jan/anna/marek/kasia/pawel @example.com` / `Password1!` |
| Produkty globalne | 24 | należą do admina, `is_global=TRUE`, widoczne w wyszukiwarce |
| Produkty prywatne | 10 | po 2 na użytkownika, `is_global=FALSE` |
| Przepisy | 11 | każdy ma składniki + automatycznie wygenerowany auto-produkt |

Uprawnienia admina: tylko admin może przełączać flagę `is_global` produktu przez
`PATCH /products/{id}/global`. W UI przycisk pojawia się na stronie produktu.

---

## Najważniejsze komendy

Backend (z katalogu `backend/`, aktywny `.venv`):

| Komenda | Opis |
|---|---|
| `uvicorn app.main:app --reload --host 127.0.0.1` | Start FastAPI z hot-reloadem (jawnie IPv4) |
| `python migrate.py` | Nakłada wszystkie nowe migracje z `migrations/` |
| `python migrate.py status` | Historia migracji i aktualna wersja bazy |
| `python migrate.py rollback` | Cofa ostatnią migrację |
| `python migrate.py rollback [ID]` | Cofa wszystkie migracje po wskazanym ID |
| `python seed.py` | Seed bazy danymi przykładowymi |

Frontend (z katalogu `frontend/`):

| Komenda | Opis |
|---|---|
| `npm run dev` | Vite dev server (port 5173) |
| `npm run build` | Build produkcyjny do `dist/` |
| `npm run preview` | Lokalny preview buildu |
