from fastapi import HTTPException
from datetime import date as DateType
from .schemas import MealItemCreate


def _find_or_create_meal(
    conn, user_id: str, meal_date: DateType, meal_type: str
) -> str:
    """Znajduje slot meals_meal dla (user, date, type) lub tworzy nowy."""
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id FROM meals_meal
            WHERE user_id = %s AND date = %s AND meal_type = %s
            """,
            (user_id, meal_date, meal_type),
        )
        existing = cursor.fetchone()
        if existing:
            return existing["id"]

        cursor.execute(
            """
            INSERT INTO meals_meal (date, meal_type, user_id)
            VALUES (%s, %s, %s) RETURNING id
            """,
            (meal_date, meal_type, user_id),
        )
        return cursor.fetchone()["id"]


def add_meal_item(conn, user_id: str, data: MealItemCreate) -> dict:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT name, quantity, fat, carbohydrates, protein, energy_kcal
            FROM products_product WHERE id = %s
            """,
            (str(data.product_id),),
        )
        product = cursor.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Produkt nie istnieje")

        meal_id = _find_or_create_meal(conn, user_id, data.date, data.meal_type)

        cursor.execute(
            """
            INSERT INTO meals_mealitem (portion, meal_id, product_id)
            VALUES (%s, %s, %s) RETURNING id
            """,
            (data.portion, meal_id, str(data.product_id)),
        )
        item_id = cursor.fetchone()["id"]

        scale = data.portion / product["quantity"]
        item_kcal = product["energy_kcal"] * scale
        # 1 kcal = 1 punkt do leaderboardu (floor zeby score byl integer >= 0)
        cursor.execute(
            "INSERT INTO leaderboard_entry (user_id, score) VALUES (%s, %s)",
            (user_id, int(item_kcal)),
        )
        conn.commit()

        return {
            "id": item_id,
            "product_id": data.product_id,
            "product_name": product["name"],
            "portion": data.portion,
            "fat": product["fat"] * scale,
            "carbohydrates": product["carbohydrates"] * scale,
            "protein": product["protein"] * scale,
            "energy_kcal": product["energy_kcal"] * scale,
        }


def delete_meal_item(conn, user_id: str, item_id) -> bool:
    iid = str(item_id)
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT m.user_id FROM meals_mealitem mi
            JOIN meals_meal m ON m.id = mi.meal_id
            WHERE mi.id = %s
            """,
            (iid,),
        )
        owner = cursor.fetchone()
        if not owner:
            return False
        if str(owner["user_id"]) != str(user_id):
            raise HTTPException(status_code=403, detail="To nie jest twoja pozycja")

        cursor.execute("DELETE FROM meals_mealitem WHERE id = %s", (iid,))
        # jesli slot zostal pusty, sprzatamy go zeby nie zostawac smieci w meals_meal
        cursor.execute(
            """
            DELETE FROM meals_meal m
            WHERE m.user_id = %s
              AND NOT EXISTS (SELECT 1 FROM meals_mealitem WHERE meal_id = m.id)
            """,
            (user_id,),
        )
        conn.commit()
        return True


def list_meals_for_day(conn, user_id: str, day: DateType) -> list:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT m.id, m.date, m.meal_type,
                   mi.id AS item_id, mi.portion, mi.product_id,
                   p.name AS product_name, p.quantity AS product_quantity,
                   p.fat, p.carbohydrates, p.protein, p.energy_kcal
            FROM meals_meal m
            LEFT JOIN meals_mealitem mi ON mi.meal_id = m.id
            LEFT JOIN products_product p ON p.id = mi.product_id
            WHERE m.user_id = %s AND m.date = %s
            ORDER BY m.meal_type, mi.id
            """,
            (user_id, day),
        )
        rows = cursor.fetchall()

    meals_by_id: dict = {}
    for row in rows:
        meal_id = row["id"]
        if meal_id not in meals_by_id:
            meals_by_id[meal_id] = {
                "id": meal_id,
                "date": row["date"],
                "meal_type": row["meal_type"],
                "items": [],
            }
        if row["item_id"] is not None:
            scale = row["portion"] / row["product_quantity"]
            meals_by_id[meal_id]["items"].append(
                {
                    "id": row["item_id"],
                    "product_id": row["product_id"],
                    "product_name": row["product_name"],
                    "portion": row["portion"],
                    "fat": row["fat"] * scale,
                    "carbohydrates": row["carbohydrates"] * scale,
                    "protein": row["protein"] * scale,
                    "energy_kcal": row["energy_kcal"] * scale,
                }
            )
    return list(meals_by_id.values())
