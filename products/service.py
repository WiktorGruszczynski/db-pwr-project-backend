from uuid import uuid4
import schemas


def create_product(db, product: schemas.ProductCreate):

    # Sprawdzenie czy produkt o identycznej nazwie i kaloryczności istnieje
    cur = db.cursor()
    check_sql = "SELECT * FROM products_product WHERE name = %s AND energy_kcal = %s"
    cur.execute(check_sql, (product.name, product.energy_kcal))
    existing_product = cur.fetchone()

    if existing_product:
        # Jeśli produkt już jest, po prostu go zwracamy i nie dodajemy nowego
        return existing_product

    # DODAWANIE NOWEGO (jeśli nie znaleziono duplikatu)
    product_id = str(uuid4())
    sql = """
          INSERT INTO products_product (id, name, quantity, quantity_unit, energy_kcal, \
                                        fat, saturated_fat, carbohydrates, sugars, \
                                        fiber, protein, salt) \
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING * \
          """
    values = (
        product_id,
        product.name,
        product.quantity,
        product.quantity_unit,
        product.energy_kcal,
        product.fat,
        product.saturated_fat,
        product.carbohydrates,
        product.sugars,
        product.fiber,
        product.protein,
        product.salt,
    )

    cur.execute(sql, values)
    new_product = cur.fetchone()
    db.commit()
    return new_product


def get_product(db, product_id):
    cursor = db.cursor()
    query = "SELECT * FROM products_product WHERE id = %s"
    cursor.execute(query, (str(product_id),))
    product = cursor.fetchone()
    cursor.close()
    return product


def delete_product(db, product_id):
    cursor = db.cursor()
    query = "DELETE FROM products_product WHERE id = %s"
    cursor.execute(query, (str(product_id),))
    affected_rows = cursor.rowcount
    db.commit()
    cursor.close()
    return affected_rows > 0


def patch_product(db, product_id: str, product_data):
    cursor = db.cursor()
    update_data = product_data.model_dump(exclude_unset=True)

    if not update_data:
        return None  # Nic nie przesłano do zmiany
    columns = ", ".join([f"{key} = %s" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(str(product_id))
    sql = f"UPDATE products_product SET {columns} WHERE id = %s RETURNING *"

    try:
        cursor.execute(sql, values)
        updated_product = cursor.fetchone()
        db.commit()
        return updated_product
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
