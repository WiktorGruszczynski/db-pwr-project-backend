from fastapi import HTTPException
from .schemas import ProductCreate, ProductUpdate


def create_product(conn, product: ProductCreate, user_id: str):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM products_product
            WHERE name = %s AND energy_kcal = %s AND user_id = %s
            """,
            (product.name, product.energy_kcal, user_id),
        )
        existing_product = cursor.fetchone()

        if existing_product:
            return existing_product

        cursor.execute(
            """
            INSERT INTO products_product (name, quantity, quantity_unit,
                                          fat, carbohydrates, protein,
                                          energy_kcal, user_id,
                                          is_global, recipe_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FALSE, NULL) RETURNING *
            """,
            (
                product.name,
                product.quantity,
                product.quantity_unit,
                product.fat,
                product.carbohydrates,
                product.protein,
                product.energy_kcal,
                user_id,
            ),
        )
        new_product = cursor.fetchone()
        conn.commit()
        return new_product


def search_global_products(conn, query: str):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM products_product
            WHERE is_global = TRUE AND name ILIKE %s
            ORDER BY name
            """,
            (f"%{query}%",),
        )
        return cursor.fetchall()


def list_user_products(conn, user_id: str):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM products_product
            WHERE is_global = FALSE AND user_id = %s
            ORDER BY name
            """,
            (user_id,),
        )
        return cursor.fetchall()


def get_product(conn, product_id):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM products_product WHERE id = %s",
            (str(product_id),),
        )
        return cursor.fetchone()


def delete_product(conn, product_id):
    with conn.cursor() as cursor:
        cursor.execute(
            "DELETE FROM products_product WHERE id = %s",
            (str(product_id),),
        )
        affected_rows = cursor.rowcount
        conn.commit()
        return affected_rows > 0


def set_product_global(conn, product_id, is_global: bool):
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE products_product SET is_global = %s WHERE id = %s RETURNING *",
            (is_global, str(product_id)),
        )
        updated = cursor.fetchone()
        conn.commit()
        return updated


def patch_product(conn, product_id: str, product_data: ProductUpdate):
    update_data = product_data.model_dump(exclude_unset=True)

    if not update_data:
        return None

    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT recipe_id FROM products_product WHERE id = %s",
            (str(product_id),),
        )
        existing = cursor.fetchone()
        if not existing:
            return None
        if existing["recipe_id"] is not None:
            raise HTTPException(
                status_code=409,
                detail="Tego produktu nie mozna edytowac bezposrednio - "
                "jest powiazany z przepisem. Edytuj go przez PATCH /recipes/{id}.",
            )

        columns = ", ".join([f"{key} = %s" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(str(product_id))
        sql = f"UPDATE products_product SET {columns} WHERE id = %s RETURNING *"

        cursor.execute(sql, values)
        updated_product = cursor.fetchone()
        conn.commit()
        return updated_product
