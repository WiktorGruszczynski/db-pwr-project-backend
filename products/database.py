import psycopg2
from psycopg2.extras import RealDictCursor

DB_PARAMS = {
    "dbname": "food_app",
    "user": "postgres",
    "password": "Pawel2005",
    "host": "localhost",
    "port": "5432"
}

def get_db():
    conn = psycopg2.connect(**DB_PARAMS, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()