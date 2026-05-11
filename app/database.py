import os
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from dotenv import load_dotenv
from contextlib import contextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class DatabaseManager:
    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            try:
                cls._pool = pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=10,  # Dostosuj do potrzeb Twojej aplikacji
                    host=os.getenv("DB_HOST"),
                    database=os.getenv("DB_NAME"),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    port=os.getenv("DB_PORT", "5432"),
                    cursor_factory=RealDictCursor,
                )
                logger.info("Połączono z bazą danych (pula utworzona).")
            except Exception as e:
                logger.error(f"Błąd podczas tworzenia puli połączeń: {e}")
                raise e
        return cls._pool

    @classmethod
    @contextmanager
    def get_connection(cls):
        """Context manager do bezpiecznego pobierania połączenia z puli."""
        connection_pool = cls.get_pool()
        conn = connection_pool.getconn()
        try:
            yield conn
            conn.commit()  # Automatyczny commit po sukcesie
        except Exception as e:
            conn.rollback()  # Rollback w razie błędu
            logger.error(f"Błąd bazy danych: {e}")
            raise
        finally:
            connection_pool.putconn(conn)


def get_db():
    with DatabaseManager.get_connection() as conn:
        yield conn
