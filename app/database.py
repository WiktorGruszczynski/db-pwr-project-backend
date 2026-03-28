import psycopg2
import os
from psycopg2.extras import RealDictCursor


def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT"),
            cursor_factory=RealDictCursor,  # wyniki kwerend wracają jako słowniki
        )
        return connection
    except Exception as e:
        print(f"Could not connect to database: {e}")
        raise e
