# Nutrition App - DB project

---

## 📖 O projekcie

Aplikacja żywieniowa


## 🚀 Uruchomienie lokalne

### Wymagania

- Python **3.10+**
- pip

### Instalacja

1. **Sklonuj repozytorium**

    ```bash
    git clone https://github.com/WiktorGruszczynski/db-pwr-project-backend.git
    cd db-pwr-project-backend
    ```

2. **Utwórz i aktywuj środowisko wirtualne**

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Linux / macOS
   .venv\Scripts\activate           # Windows
   ```

3. **Zainstaluj zależności**

   ```bash
   pip install -r requirements.txt
   ```

4. **Skopiuj plik środowiskowy**

   ```
   cp .env.example .env
   ```

Po uruchomieniu API będzie dostępne pod:
[http://localhost:8000/](http://localhost:8000/)

---

## 📜 Najważniejsze komendy

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
