# Nutrition App - DB project

---

## 📖 O projekcie

Aplikacja żywieniowa — monorepo z backendem (FastAPI) i frontendem (React + Vite).

```
.
├── backend/    # FastAPI + Postgres
└── frontend/   # React + Vite (dev proxy → backend)
```


## 🚀 Uruchomienie lokalne

### Backend

Wymagania: Python **3.10+**, pip.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows
pip install -r requirements.txt
cp .env.example .env             # i uzupełnij wartości
python migrate.py                # nałóż migracje
uvicorn app.main:app --reload    # API na http://localhost:8000
```

API: [http://localhost:8000/](http://localhost:8000/)
Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Frontend

Wymagania: Node **18+**, npm.

```bash
cd frontend
npm install
npm run dev
```

Aplikacja: [http://localhost:5173/](http://localhost:5173/)

Frontend w trybie dev używa proxy Vite na ścieżkach `/auth`, `/users`, `/products`, `/recipes`, `/meals`, `/leaderboard` → `http://localhost:8000`. Backend dodatkowo ma CORS z `allow_credentials=True` dla `http://localhost:5173`.

---

## 📜 Najważniejsze komendy

Komendy backendu uruchamiamy z katalogu `backend/`.

* **`uvicorn app.main:app --reload`** – Uruchamia serwer deweloperski FastAPI z automatycznym odświeżaniem kodu.
* **`python migrate.py`** – Nakłada wszystkie nowe migracje z folderu `/migrations` na bazę danych.
* **`python migrate.py status`** – Wyświetla historię nałożonych migracji oraz wskazuje obecną wersję bazy.
* **`python migrate.py rollback`** – Cofa tylko ostatnią (jedną) nałożoną migrację.
* **`python migrate.py rollback [ID]`** – Cofa wszystkie migracje, które zostały nałożone po wskazanym identyfikatorze `[ID]`.


#### Examples:

```bash
# Check current database version
python apply_migrations.py status

# Rollback to specific version (e.g., 0000_init)
python apply_migrations.py rollback 0000_init
```

---


## 🛠️ Jak kontrybuować (Git Workflow)

Aby zachować porządek w projekcie i uniknąć konfliktów, stosujemy model pracy oparty na gałęziach (Feature Branches). **Nigdy nie pushujemy bezpośrednio do gałęzi `main`.**

### Kroki do wykonania przy nowym zadaniu:

1.  **Zaktualizuj lokalny projekt**
    Przełącz się na main i pobierz najnowsze zmiany od innych:
    ```bash
    git checkout main
    git pull origin main
    ```

2.  **Stwórz nowy branch**
    ```bash
    git checkout -b nazwa-twojego-brancha
    ```

3.  **Wprowadź zmiany i zrób commit**
    Pamiętaj o zachowaniu standardu [**Conventional Commits**](#-format-commitów).
    ```bash
    git add .
    git commit -m "feat(db): add users table schema"
    ```

4.  **Wyślij zmiany na GitHub**
    ```bash
    git push -u origin nazwa-twojego-brancha
    ```

5.  **Stwórz Pull Request**

---


### 🧹 Pre-commit i jakość kodu

W projekcie używamy [pre-commit](https://pre-commit.com/) oraz [ruff](https://docs.astral.sh/ruff/) do automatycznego formatowania i lintowania kodu przy każdym `git commit`.

**Instalacja narzędzi deweloperskich**

   ```bash
      pip install -r requirements-dev.txt
   ```

**Instalacja hooków pre-commit**

   ```bash
      pre-commit install
   ```

**Ręczne uruchomienie wszystkich hooków**

   ```bash
      pre-commit run --all-files
   ```


Po instalacji hooków, przy każdym `git commit` automatycznie uruchomią się:

- `ruff` – linting i sortowanie importów

- `ruff-format` – formatowanie kodu


### ✍️ Format commitów

Stosujemy standard [**Conventional Commits**](https://www.conventionalcommits.org/en/v1.0.0/), aby się móc później łatwiej połapać.

**Format**

```
<type>(opcjonalny scope): opis w czasie teraźniejszym
```

**Typy commitów**

- `feat:` - nowa funkcjonalność
- `fix:` - naprawa błędu
- `docs:` - dokumentacja
- `refactor:` - poprawa struktury kodu
- `test:` - testy
- `chore:` - zmiany w konfiguracji, dependency itp.

**Przykłady**

```bash
   feat(auth): add USOS SSO login
   fix(quizzes): correct question ordering
   docs: update README with backend setup
```
---
