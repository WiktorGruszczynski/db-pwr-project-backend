# Nutrition App

Aplikacja żywieniowa — monorepo z backendem (FastAPI + PostgreSQL) i frontendem (React + Vite).

```
.
├── backend/      # FastAPI, migracje, seed
│   ├── app/      # kod aplikacji
│   ├── migrations/
│   ├── migrate.py
│   ├── seed.py   # skrypt seedujący bazę
│   └── requirements.txt
└── frontend/     # React + Vite (dev proxy → backend)
```

---

## 🚀 Uruchomienie lokalne

### 1. Backend

**Wymagania:** Python **3.10+**, pip, działająca instancja PostgreSQL.

```bash
cd backend

# utworzenie i aktywacja środowiska wirtualnego
python -m venv .venv
.venv\Scripts\activate           # Windows
source .venv/bin/activate        # Linux / macOS

# instalacja zależności
pip install -r requirements.txt

# konfiguracja .env (uzupełnij DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT, SMTP_*)
cp .env.example .env

# migracje
python migrate.py

# (opcjonalnie) dane przykładowe — patrz sekcja Seed
python seed.py

# start serwera (jawnie IPv4 — patrz notka o sieci lokalnej ponizej)
uvicorn app.main:app --reload --host 127.0.0.1
```

- API: <http://localhost:8000/>
- Swagger UI: <http://localhost:8000/docs>

> **ℹ️ Sieć lokalna na Windows (localhost = IPv4 vs IPv6).** `localhost` rozwiązuje się i na `127.0.0.1` (IPv4), i na `::1` (IPv6) — a różne programy próbują ich w różnej kolejności (Firefox najpierw IPv4, Node/Python często IPv6). Jeśli usługa słucha tylko na jednej rodzinie, połączenie w drugą jest na Windows **cicho upuszczane** i klient czeka 0,25–2 s na timeout/fallback. Dlatego cały stack jest jawnie spięty po IPv4:
> - **Backend**: `uvicorn --host 127.0.0.1`
> - **Vite**: `server.host: '127.0.0.1'`, proxy → `http://127.0.0.1:8000`
> - **Baza** w `.env`: `DB_HOST=127.0.0.1` (PostgreSQL domyślnie słucha na IPv4)
>
> W przeglądarce nadal otwierasz <http://localhost:5173/> — to działa, bo przeglądarki sprawnie wybierają IPv4. Nie mieszaj rodzin (np. backend na `::1` przy froncie na `127.0.0.1`), bo wracają sekundowe opóźnienia.

### 2. Frontend

**Wymagania:** Node **18+**, npm.

```bash
cd frontend
npm install
npm run dev
```

- Aplikacja: <http://localhost:5173/>

Frontend w trybie dev używa **proxy Vite**: wszystkie wywołania API idą pod prefiksem `/api`, a Vite przekierowuje tylko `/api/*` → `http://localhost:8000` (zdejmując prefiks `/api` przed przekazaniem do backendu). Dzięki temu nazwy tras SPA (`/recipes`, `/products`, `/meals`, `/leaderboard`, …) **nie kolidują** z proxy i odświeżenie dowolnej podstrony serwuje aplikację zamiast przekierowywać na backend. Cookie sesji (httpOnly, SameSite=Lax) działa bez konfiguracji CORS po stronie przeglądarki. Backend dodatkowo ma `CORSMiddleware` z `allow_credentials=True` dla `http://localhost:5173` (na wypadek bezpośrednich wywołań).

---

## 🌱 Seed (dane przykładowe)

Skrypt `backend/seed.py` wstawia do bazy gotowy zestaw użytkowników, produktów i przepisów. Jest **idempotentny** — pomija rekordy już istniejące.

```bash
cd backend
python seed.py                          # admin z domyślnym mailem
python seed.py --admin-email mail@x.pl  # własny e-mail dla admina
```

**Co tworzy:**

| Typ | Ilość | Szczegóły |
|---|---|---|
| Admin | 1 | `admin@nutrition.local` / `Admin123!` (rola `ADMIN`) |
| Użytkownicy | 5 | `jan/anna/marek/kasia/pawel @example.com` / `Password1!` |
| Produkty globalne | 10 | należą do admina, `is_global=TRUE`, widoczne w wyszukiwarce |
| Produkty prywatne | 10 | po 2 na użytkownika, `is_global=FALSE` |
| Przepisy | 5 | każdy ma składniki + automatycznie wygenerowany auto-produkt |

**Uprawnienia admina:** tylko admin może przełączać flagę `is_global` produktu przez `PATCH /products/{id}/global`. W UI przycisk pojawia się na stronie produktu.

---

## 📜 Najważniejsze komendy

Komendy backendu uruchamiamy z katalogu `backend/` z aktywnym `.venv`.

| Komenda | Opis |
|---|---|
| `uvicorn app.main:app --reload --host 127.0.0.1` | Start FastAPI z hot-reloadem (jawnie IPv4 — patrz notka o sieci) |
| `python migrate.py` | Nakłada wszystkie nowe migracje z `migrations/` |
| `python migrate.py status` | Historia migracji i aktualna wersja bazy |
| `python migrate.py rollback` | Cofa ostatnią migrację |
| `python migrate.py rollback [ID]` | Cofa wszystkie migracje po wskazanym ID |
| `python seed.py` | Seed bazy danymi przykładowymi |

Komendy frontendu z katalogu `frontend/`:

| Komenda | Opis |
|---|---|
| `npm run dev` | Vite dev server (port 5173) |
| `npm run build` | Build produkcyjny do `dist/` |
| `npm run preview` | Lokalny preview buildu |

---

## 🛠️ Git Workflow

Stosujemy model **Feature Branches**. **Nigdy nie pushujemy bezpośrednio do `main`.**

1. **Zaktualizuj `main`:**
   ```bash
   git checkout main
   git pull origin main
   ```
2. **Nowy branch:**
   ```bash
   git checkout -b nazwa-twojego-brancha
   ```
3. **Commit** w standardzie [Conventional Commits](#-format-commitów):
   ```bash
   git add .
   git commit -m "feat(db): add users table schema"
   ```
4. **Push:**
   ```bash
   git push -u origin nazwa-twojego-brancha
   ```
5. **Pull Request** na GitHubie.

---

### 🧹 Pre-commit i jakość kodu

Używamy [pre-commit](https://pre-commit.com/) + [ruff](https://docs.astral.sh/ruff/) do automatycznego lintowania i formatowania przy `git commit`.

```bash
# instalacja (w aktywnym .venv backendu)
pip install pre-commit ruff
pre-commit install

# ręczne uruchomienie
pre-commit run --all-files
```

Hooki, które się odpalą przy commicie:
- `ruff` – linting i sortowanie importów
- `ruff-format` – formatowanie

---

### ✍️ Format commitów

Standard [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
<type>(opcjonalny scope): opis w czasie teraźniejszym
```

**Typy:**
- `feat:` — nowa funkcjonalność
- `fix:` — naprawa błędu
- `docs:` — dokumentacja
- `refactor:` — poprawa struktury kodu
- `test:` — testy
- `chore:` — konfiguracja, dependency itp.

**Przykłady:**
```bash
feat(auth): add USOS SSO login
fix(recipes): correct ingredient ordering
docs: update README with seed instructions
```
