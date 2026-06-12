from fastapi import HTTPException
from .schemas import RecipeCreate, RecipeUpdate, IngredientIn


def _compute_auto_product_values(conn, ingredients: list[IngredientIn]) -> dict:
    """Sumuje wartości odżywcze składników skalowane przez ilość użytą w przepisie."""
    totals = {
        "quantity": 0.0,
        "fat": 0.0,
        "carbohydrates": 0.0,
        "protein": 0.0,
        "energy_kcal": 0.0,
    }

    with conn.cursor() as cursor:
        for ing in ingredients:
            cursor.execute(
                """
                SELECT quantity, fat, carbohydrates, protein, energy_kcal
                FROM products_product WHERE id = %s
                """,
                (str(ing.product_id),),
            )
            product = cursor.fetchone()
            if not product:
                raise HTTPException(
                    status_code=400,
                    detail=f"Produkt {ing.product_id} nie istnieje",
                )

            scale = ing.quantity / product["quantity"]
            totals["quantity"] += ing.quantity
            totals["fat"] += product["fat"] * scale
            totals["carbohydrates"] += product["carbohydrates"] * scale
            totals["protein"] += product["protein"] * scale
            totals["energy_kcal"] += product["energy_kcal"] * scale

    return totals


def _insert_ingredients(conn, recipe_id: str, ingredients: list[IngredientIn]) -> None:
    with conn.cursor() as cursor:
        for ing in ingredients:
            cursor.execute(
                """
                INSERT INTO recipes_ingredient (quantity, unit, product_id, recipe_id)
                VALUES (%s, %s, %s, %s)
                """,
                (ing.quantity, ing.unit, str(ing.product_id), recipe_id),
            )


def _upsert_auto_product(
    conn, recipe_id: str, recipe_name: str, user_id: str, totals: dict
) -> str:
    """Tworzy lub aktualizuje produkt powiązany z przepisem przez recipe_id.
    Wartości odżywcze normalizowane do 100 g (konwencja produktów w bazie)."""
    total_g = totals["quantity"]
    per100 = {
        key: totals[key] * 100.0 / total_g
        for key in ("fat", "carbohydrates", "protein", "energy_kcal")
    }

    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM products_product WHERE recipe_id = %s", (recipe_id,)
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                """
                UPDATE products_product
                SET name = %s, quantity = 100, quantity_unit = 'g',
                    fat = %s, carbohydrates = %s, protein = %s, energy_kcal = %s
                WHERE id = %s RETURNING id
                """,
                (
                    recipe_name,
                    per100["fat"],
                    per100["carbohydrates"],
                    per100["protein"],
                    per100["energy_kcal"],
                    existing["id"],
                ),
            )
        else:
            cursor.execute(
                """
                INSERT INTO products_product (name, quantity, quantity_unit,
                                              fat, carbohydrates, protein, energy_kcal,
                                              user_id, is_global, recipe_id)
                VALUES (%s, 100, 'g', %s, %s, %s, %s, %s, FALSE, %s) RETURNING id
                """,
                (
                    recipe_name,
                    per100["fat"],
                    per100["carbohydrates"],
                    per100["protein"],
                    per100["energy_kcal"],
                    user_id,
                    recipe_id,
                ),
            )
        return cursor.fetchone()["id"]


def _fetch_recipe_full(conn, recipe_id: str, user_id: str | None = None) -> dict | None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT r.id, r.name, r.description, r.average_rating,
                   r.created_at, r.user_id,
                   p.id AS product_id,
                   NOT COALESCE(p.is_global, FALSE) AS is_private
            FROM recipes_recipe r
            LEFT JOIN products_product p ON p.recipe_id = r.id
            WHERE r.id = %s
            """,
            (recipe_id,),
        )
        recipe = cursor.fetchone()
        if not recipe:
            return None

        cursor.execute(
            """
            SELECT i.id, i.product_id, i.quantity, i.unit,
                   COALESCE(p.name, '(produkt usunięty)') AS product_name
            FROM recipes_ingredient i
            LEFT JOIN products_product p ON p.id = i.product_id
            WHERE i.recipe_id = %s
            ORDER BY i.id
            """,
            (recipe_id,),
        )
        recipe = dict(recipe)
        recipe["ingredients"] = [dict(row) for row in cursor.fetchall()]

        recipe["my_rating"] = None
        if user_id:
            cursor.execute(
                "SELECT rating FROM recipes_rating WHERE recipe_id = %s AND user_id = %s",
                (recipe_id, str(user_id)),
            )
            row = cursor.fetchone()
            if row:
                recipe["my_rating"] = row["rating"]
        return recipe


def create_recipe(conn, recipe: RecipeCreate, user_id: str) -> dict:
    totals = _compute_auto_product_values(conn, recipe.ingredients)

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO recipes_recipe (name, description, user_id)
            VALUES (%s, %s, %s) RETURNING id
            """,
            (recipe.name, recipe.description, user_id),
        )
        recipe_id = cursor.fetchone()["id"]

    _insert_ingredients(conn, recipe_id, recipe.ingredients)
    _upsert_auto_product(conn, recipe_id, recipe.name, user_id, totals)
    conn.commit()

    return _fetch_recipe_full(conn, recipe_id)


def search_recipes_by_name(conn, query: str) -> list[dict]:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, description, average_rating, user_id
            FROM recipes_recipe
            WHERE name ILIKE %s
            ORDER BY name
            LIMIT 20
            """,
            (f"%{query}%",),
        )
        return cursor.fetchall()


def get_recipe(conn, recipe_id, user_id: str | None = None) -> dict | None:
    return _fetch_recipe_full(conn, str(recipe_id), user_id)


def list_recipes_by_user(conn, user_id: str) -> list[dict]:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, description, average_rating, user_id
            FROM recipes_recipe
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (str(user_id),),
        )
        return cursor.fetchall()


def rate_recipe(conn, recipe_id, user_id: str, rating: int) -> dict | None:
    """Wystawia/aktualizuje ocene uzytkownika; srednia przelicza trigger w bazie."""
    rid = str(recipe_id)
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM recipes_recipe WHERE id = %s", (rid,))
        if not cursor.fetchone():
            return None

        cursor.execute(
            """
            INSERT INTO recipes_rating (rating, recipe_id, user_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (recipe_id, user_id) DO UPDATE SET rating = EXCLUDED.rating
            """,
            (rating, rid, str(user_id)),
        )
        conn.commit()

        cursor.execute(
            "SELECT average_rating FROM recipes_recipe WHERE id = %s", (rid,)
        )
        avg = cursor.fetchone()["average_rating"]
    return {"average_rating": avg or 0.0, "my_rating": rating}


def delete_recipe(conn, recipe_id, user_id: str) -> bool:
    rid = str(recipe_id)
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_id FROM recipes_recipe WHERE id = %s", (rid,))
        existing = cursor.fetchone()
        if not existing:
            return False
        if str(existing["user_id"]) != str(user_id):
            raise HTTPException(status_code=403, detail="To nie jest twój przepis")

        # auto-produkt ma FK ON DELETE SET NULL, ale chcemy go usunac razem z przepisem
        cursor.execute("DELETE FROM products_product WHERE recipe_id = %s", (rid,))
        # ingredients zostana usuniete kaskadowo
        cursor.execute("DELETE FROM recipes_recipe WHERE id = %s", (rid,))
        conn.commit()
        return True


def update_recipe(conn, recipe_id, data: RecipeUpdate, user_id: str) -> dict | None:
    rid = str(recipe_id)

    with conn.cursor() as cursor:
        cursor.execute("SELECT name, user_id FROM recipes_recipe WHERE id = %s", (rid,))
        existing = cursor.fetchone()
        if not existing:
            return None
        if str(existing["user_id"]) != str(user_id):
            raise HTTPException(status_code=403, detail="To nie jest twój przepis")

    meta = data.model_dump(exclude_unset=True, exclude={"ingredients"})
    if meta:
        columns = ", ".join([f"{k} = %s" for k in meta.keys()])
        values = list(meta.values()) + [rid]
        with conn.cursor() as cursor:
            cursor.execute(f"UPDATE recipes_recipe SET {columns} WHERE id = %s", values)

    if data.ingredients is not None:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM recipes_ingredient WHERE recipe_id = %s", (rid,)
            )
        _insert_ingredients(conn, rid, data.ingredients)
        totals = _compute_auto_product_values(conn, data.ingredients)
        new_name = meta.get("name", existing["name"])
        _upsert_auto_product(conn, rid, new_name, user_id, totals)
    elif "name" in meta:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE products_product SET name = %s WHERE recipe_id = %s",
                (meta["name"], rid),
            )

    conn.commit()
    return _fetch_recipe_full(conn, rid)
