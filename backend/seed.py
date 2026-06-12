"""
Skrypt seedujący bazę danych danymi przykładowymi.
Uruchom z katalogu backend/:

    python seed.py

Wymagania: aktywne .venv, uzupełniony .env z danymi bazy.
"""

import os
import sys

# Dodaj katalog backend/ do PYTHONPATH, by importy z `app.*` działały.
# Importy poniżej celowo nie są na górze pliku — wymagają ustawionego
# sys.path i załadowanych zmiennych środowiskowych.
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

import bcrypt  # noqa: E402
import psycopg2  # noqa: E402
import psycopg2.extras  # noqa: E402
from app.recipes.schemas import RecipeCreate, IngredientIn  # noqa: E402
from app.recipes.service import create_recipe  # noqa: E402

# ─────────────────────────────────────────────
# Połączenie z bazą
# ─────────────────────────────────────────────


def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432"),
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


def hash_pw(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


# ─────────────────────────────────────────────
# Dane seedowe
# ─────────────────────────────────────────────

ADMIN = {
    "username": "admin",
    "email": "admin@nutrition.local",
    "password": "Admin123!",
    "role": "ADMIN",
}

USERS = [
    {"username": "jan_kowalski", "email": "jan@example.com", "password": "Password1!"},
    {"username": "anna_nowak", "email": "anna@example.com", "password": "Password1!"},
    {
        "username": "marek_wisniewski",
        "email": "marek@example.com",
        "password": "Password1!",
    },
    {
        "username": "kasia_zielinska",
        "email": "kasia@example.com",
        "password": "Password1!",
    },
    {
        "username": "pawel_wojcik",
        "email": "pawel@example.com",
        "password": "Password1!",
    },
]

# Produkty globalne (tworzone przez admina, is_global=TRUE)
# Wartości odżywcze na 100 g
GLOBAL_PRODUCTS = [
    {
        "name": "Kurczak pierś",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 3.6,
        "carbohydrates": 0.0,
        "protein": 31.0,
        "energy_kcal": 165,
    },
    {
        "name": "Ryż biały gotowany",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 0.3,
        "carbohydrates": 28.2,
        "protein": 2.7,
        "energy_kcal": 130,
    },
    {
        "name": "Jajko kurze (całe)",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 9.5,
        "carbohydrates": 0.6,
        "protein": 12.6,
        "energy_kcal": 143,
    },
    {
        "name": "Mleko 3,2%",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 3.2,
        "carbohydrates": 4.8,
        "protein": 3.2,
        "energy_kcal": 61,
    },
    {
        "name": "Chleb pszenny",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 3.2,
        "carbohydrates": 49.4,
        "protein": 8.9,
        "energy_kcal": 265,
    },
    {
        "name": "Łosoś atlantycki",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 13.4,
        "carbohydrates": 0.0,
        "protein": 20.4,
        "energy_kcal": 208,
    },
    {
        "name": "Banan",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 0.3,
        "carbohydrates": 22.8,
        "protein": 1.1,
        "energy_kcal": 89,
    },
    {
        "name": "Jabłko",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 0.2,
        "carbohydrates": 13.8,
        "protein": 0.3,
        "energy_kcal": 52,
    },
    {
        "name": "Brokuł",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 0.4,
        "carbohydrates": 6.6,
        "protein": 2.8,
        "energy_kcal": 34,
    },
    {
        "name": "Makaron pszenny",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 1.3,
        "carbohydrates": 74.7,
        "protein": 13.0,
        "energy_kcal": 371,
    },
    {
        "name": "Wołowina (polędwica)",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 6.0,
        "carbohydrates": 0.0,
        "protein": 22.0,
        "energy_kcal": 150,
    },
    {
        "name": "Ryż brązowy gotowany",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 0.9,
        "carbohydrates": 23.0,
        "protein": 2.6,
        "energy_kcal": 111,
    },
    {
        "name": "Ziemniaki gotowane",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 0.1,
        "carbohydrates": 17.0,
        "protein": 2.0,
        "energy_kcal": 77,
    },
    {
        "name": "Marchew",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 0.2,
        "carbohydrates": 9.6,
        "protein": 0.9,
        "energy_kcal": 41,
    },
    {
        "name": "Cebula",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 0.1,
        "carbohydrates": 9.3,
        "protein": 1.1,
        "energy_kcal": 40,
    },
    {
        "name": "Ser żółty Gouda",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 27.4,
        "carbohydrates": 0.0,
        "protein": 25.0,
        "energy_kcal": 356,
    },
    {
        "name": "Migdały",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 49.9,
        "carbohydrates": 21.6,
        "protein": 21.2,
        "energy_kcal": 579,
    },
    {
        "name": "Awokado",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 14.7,
        "carbohydrates": 8.5,
        "protein": 2.0,
        "energy_kcal": 160,
    },
    {
        "name": "Ogórek",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 0.1,
        "carbohydrates": 3.6,
        "protein": 0.7,
        "energy_kcal": 15,
    },
    {
        "name": "Papryka czerwona",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 0.3,
        "carbohydrates": 6.0,
        "protein": 1.0,
        "energy_kcal": 31,
    },
    {
        "name": "Fasola czerwona gotowana",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 0.5,
        "carbohydrates": 22.8,
        "protein": 8.7,
        "energy_kcal": 127,
    },
    {
        "name": "Miód pszczeli",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 0.0,
        "carbohydrates": 82.4,
        "protein": 0.3,
        "energy_kcal": 304,
    },
    {
        "name": "Tofu naturalne",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 4.8,
        "carbohydrates": 1.9,
        "protein": 8.0,
        "energy_kcal": 76,
    },
    {
        "name": "Twaróg półtłusty",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 4.7,
        "carbohydrates": 3.5,
        "protein": 18.0,
        "energy_kcal": 133,
    },
]

# Produkty prywatne (tworzone przez różnych userów, is_global=FALSE)
# (user_idx: 0-4 wskazuje na USERS listę)
PRIVATE_PRODUCTS = [
    {
        "user_idx": 0,
        "name": "Jogurt grecki 0%",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 0.4,
        "carbohydrates": 4.0,
        "protein": 10.0,
        "energy_kcal": 59,
    },
    {
        "user_idx": 0,
        "name": "Płatki owsiane górskie",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 6.9,
        "carbohydrates": 62.0,
        "protein": 11.0,
        "energy_kcal": 350,
    },
    {
        "user_idx": 1,
        "name": "Pierś z indyka",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 1.0,
        "carbohydrates": 0.0,
        "protein": 29.0,
        "energy_kcal": 135,
    },
    {
        "user_idx": 1,
        "name": "Ser mozzarella",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 22.4,
        "carbohydrates": 0.6,
        "protein": 18.0,
        "energy_kcal": 280,
    },
    {
        "user_idx": 2,
        "name": "Szpinak świeży",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 0.4,
        "carbohydrates": 3.6,
        "protein": 2.9,
        "energy_kcal": 23,
    },
    {
        "user_idx": 2,
        "name": "Masło orzechowe",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 50.0,
        "carbohydrates": 20.0,
        "protein": 25.0,
        "energy_kcal": 588,
    },
    {
        "user_idx": 3,
        "name": "Oliwa z oliwek",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 100.0,
        "carbohydrates": 0.0,
        "protein": 0.0,
        "energy_kcal": 884,
    },
    {
        "user_idx": 3,
        "name": "Pomidor",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 0.2,
        "carbohydrates": 3.9,
        "protein": 0.9,
        "energy_kcal": 18,
    },
    {
        "user_idx": 4,
        "name": "Tuńczyk w sosie wł.",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 0.5,
        "carbohydrates": 0.0,
        "protein": 24.0,
        "energy_kcal": 103,
    },
    {
        "user_idx": 4,
        "name": "Kasza gryczana",
        "quantity": 100,
        "quantity_unit": "g",
        "fat": 3.4,
        "carbohydrates": 71.5,
        "protein": 13.3,
        "energy_kcal": 343,
    },
]

# Przepisy: każdy ma składniki wskazujące na produkty globalne (po nazwie)
RECIPES = [
    {
        "user_idx": 0,
        "name": "Kurczak z ryżem",
        "description": "Klasyczny posiłek wysokobiałkowy. Gotowany kurczak z ryżem.",
        "ingredients": [
            {"product_name": "Kurczak pierś", "quantity": 200.0},
            {"product_name": "Ryż biały gotowany", "quantity": 150.0},
            {"product_name": "Brokuł", "quantity": 100.0},
        ],
    },
    {
        "user_idx": 1,
        "name": "Owsianka bananowa",
        "description": "Pyszna owsianka z bananem — idealna na śniadanie.",
        "ingredients": [
            {"product_name": "Płatki owsiane górskie", "quantity": 80.0},
            {"product_name": "Banan", "quantity": 120.0},
            {"product_name": "Mleko 3,2%", "quantity": 200.0},
        ],
    },
    {
        "user_idx": 2,
        "name": "Łosoś z warzywami",
        "description": "Pieczony łosoś z brokułem i ryżem.",
        "ingredients": [
            {"product_name": "Łosoś atlantycki", "quantity": 150.0},
            {"product_name": "Brokuł", "quantity": 120.0},
            {"product_name": "Ryż biały gotowany", "quantity": 100.0},
        ],
    },
    {
        "user_idx": 3,
        "name": "Omlet z warzywami",
        "description": "Szybki i pożywny omlet.",
        "ingredients": [
            {"product_name": "Jajko kurze (całe)", "quantity": 200.0},
            {"product_name": "Szpinak świeży", "quantity": 50.0},
            {"product_name": "Pomidor", "quantity": 80.0},
        ],
    },
    {
        "user_idx": 4,
        "name": "Kanapka z łososiem",
        "description": "Kanapka na chleb pszennym z łososiem.",
        "ingredients": [
            {"product_name": "Chleb pszenny", "quantity": 80.0},
            {"product_name": "Łosoś atlantycki", "quantity": 80.0},
            {"product_name": "Ser mozzarella", "quantity": 40.0},
        ],
    },
    {
        "user_idx": 0,
        "name": "Wołowina z ziemniakami",
        "description": "Sycący obiad: pieczona polędwica wołowa z ziemniakami i marchewką.",
        "ingredients": [
            {"product_name": "Wołowina (polędwica)", "quantity": 200.0},
            {"product_name": "Ziemniaki gotowane", "quantity": 250.0},
            {"product_name": "Marchew", "quantity": 100.0},
        ],
    },
    {
        "user_idx": 1,
        "name": "Koktajl bananowo-migdałowy",
        "description": "Energetyczny koktajl na mleku z bananem, migdałami i miodem.",
        "ingredients": [
            {"product_name": "Mleko 3,2%", "quantity": 250.0},
            {"product_name": "Banan", "quantity": 120.0},
            {"product_name": "Migdały", "quantity": 30.0},
            {"product_name": "Miód pszczeli", "quantity": 20.0},
        ],
    },
    {
        "user_idx": 2,
        "name": "Tofu z ryżem brązowym",
        "description": "Wegetariański obiad: tofu z ryżem brązowym i brokułem.",
        "ingredients": [
            {"product_name": "Tofu naturalne", "quantity": 150.0},
            {"product_name": "Ryż brązowy gotowany", "quantity": 150.0},
            {"product_name": "Brokuł", "quantity": 100.0},
        ],
    },
    {
        "user_idx": 3,
        "name": "Sałatka warzywna z awokado",
        "description": "Lekka sałatka z ogórka, papryki, marchewki i awokado.",
        "ingredients": [
            {"product_name": "Ogórek", "quantity": 100.0},
            {"product_name": "Papryka czerwona", "quantity": 100.0},
            {"product_name": "Marchew", "quantity": 80.0},
            {"product_name": "Awokado", "quantity": 60.0},
        ],
    },
    {
        "user_idx": 4,
        "name": "Kanapka z serem żółtym",
        "description": "Prosta kanapka: chleb pszenny, ser gouda i ogórek.",
        "ingredients": [
            {"product_name": "Chleb pszenny", "quantity": 80.0},
            {"product_name": "Ser żółty Gouda", "quantity": 40.0},
            {"product_name": "Ogórek", "quantity": 50.0},
        ],
    },
    {
        "user_idx": 0,
        "name": "Chili con carne",
        "description": "Wołowina z czerwoną fasolą, cebulą i papryką.",
        "ingredients": [
            {"product_name": "Wołowina (polędwica)", "quantity": 150.0},
            {"product_name": "Fasola czerwona gotowana", "quantity": 150.0},
            {"product_name": "Cebula", "quantity": 50.0},
            {"product_name": "Papryka czerwona", "quantity": 80.0},
        ],
    },
]


# ─────────────────────────────────────────────
# Funkcje pomocnicze
# ─────────────────────────────────────────────


def insert_user(cur, username, email, password, role="USER"):
    cur.execute(
        "SELECT id FROM users_user WHERE email = %s OR username = %s", (email, username)
    )
    existing = cur.fetchone()
    if existing:
        print(f"  [skip] użytkownik {username} już istnieje")
        return existing["id"]
    hashed = hash_pw(password)
    cur.execute(
        """
        INSERT INTO users_user (username, email, password, role, is_enabled)
        VALUES (%s, %s, %s, %s, TRUE) RETURNING id
        """,
        (username, email, hashed, role),
    )
    uid = cur.fetchone()["id"]
    print(f"  [OK]   użytkownik {username} ({role})")
    return uid


def insert_product(
    cur,
    name,
    quantity,
    quantity_unit,
    fat,
    carbohydrates,
    protein,
    energy_kcal,
    user_id,
    is_global,
):
    cur.execute(
        "SELECT id FROM products_product WHERE name = %s AND user_id = %s",
        (name, str(user_id)),
    )
    if cur.fetchone():
        print(f"  [skip] produkt '{name}' już istnieje")
        return
    cur.execute(
        """
        INSERT INTO products_product
            (name, quantity, quantity_unit, fat, carbohydrates, protein, energy_kcal, user_id, is_global)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """,
        (
            name,
            quantity,
            quantity_unit,
            fat,
            carbohydrates,
            protein,
            energy_kcal,
            str(user_id),
            is_global,
        ),
    )
    pid = cur.fetchone()["id"]
    print(f"  [OK]   produkt '{name}' (global={is_global})")
    return pid


def get_product_id_by_name(cur, name):
    cur.execute("SELECT id FROM products_product WHERE name = %s LIMIT 1", (name,))
    row = cur.fetchone()
    if not row:
        raise ValueError(
            f"Nie znaleziono produktu '{name}' — uruchom seed od nowa lub sprawdź dane."
        )
    return row["id"]


# ─────────────────────────────────────────────
# Główna logika
# ─────────────────────────────────────────────


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Seed bazy danych Nutrition App")
    parser.add_argument(
        "--admin-email",
        default=ADMIN["email"],
        help=f"E-mail konta admina (domyslnie: {ADMIN['email']})",
    )
    args = parser.parse_args()
    ADMIN["email"] = args.admin_email

    conn = get_conn()
    cur = conn.cursor()

    print("\n=== Użytkownicy ===")
    admin_id = insert_user(
        cur, ADMIN["username"], ADMIN["email"], ADMIN["password"], role="ADMIN"
    )
    user_ids = []
    for u in USERS:
        uid = insert_user(cur, u["username"], u["email"], u["password"])
        user_ids.append(uid)
    conn.commit()

    print("\n=== Produkty globalne (admin) ===")
    for p in GLOBAL_PRODUCTS:
        insert_product(
            cur,
            p["name"],
            p["quantity"],
            p["quantity_unit"],
            p["fat"],
            p["carbohydrates"],
            p["protein"],
            p["energy_kcal"],
            admin_id,
            is_global=True,
        )
    conn.commit()

    print("\n=== Produkty prywatne (użytkownicy) ===")
    for p in PRIVATE_PRODUCTS:
        uid = user_ids[p["user_idx"]]
        insert_product(
            cur,
            p["name"],
            p["quantity"],
            p["quantity_unit"],
            p["fat"],
            p["carbohydrates"],
            p["protein"],
            p["energy_kcal"],
            uid,
            is_global=False,
        )
    conn.commit()

    print("\n=== Przepisy ===")
    for r in RECIPES:
        uid = user_ids[r["user_idx"]]
        # Sprawdź czy przepis już istnieje
        cur.execute(
            "SELECT id FROM recipes_recipe WHERE name = %s AND user_id = %s",
            (r["name"], str(uid)),
        )
        if cur.fetchone():
            print(f"  [skip] przepis '{r['name']}' już istnieje")
            continue

        # Zbierz ID składników
        ingredients = []
        for ing in r["ingredients"]:
            pid = get_product_id_by_name(cur, ing["product_name"])
            ingredients.append(
                IngredientIn(product_id=pid, quantity=ing["quantity"], unit="g")
            )

        recipe_data = RecipeCreate(
            name=r["name"],
            description=r["description"],
            ingredients=ingredients,
        )
        created = create_recipe(conn, recipe_data, str(uid))
        print(
            f"  [OK]   przepis '{r['name']}' (auto-produkt id={created['product_id']})"
        )

    cur.close()
    conn.close()
    print("\n[DONE] Seedowanie zakonczone!\n")
    print("Dane logowania:")
    print("  Admin:   admin@nutrition.local  /  Admin123!")
    for u in USERS:
        print(f"  User:    {u['email']}  /  Password1!")


if __name__ == "__main__":
    main()
