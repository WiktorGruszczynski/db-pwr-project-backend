import uuid
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException
from app.database import get_db_connection
from app.users.schemas import UserRegister, UserLogin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_session_id() -> str:
    return str(uuid.uuid4())


def get_session_expiration() -> datetime:
    return datetime.now() + timedelta(days=7)


def register_new_user(user: UserRegister) -> None:
    """Sprawdza, czy użytkownik istnieje, i dodaje go do bazy."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE email = %s OR username = %s",
                (user.email, user.username),
            )
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Użytkownik już istnieje")

            hashed_password = get_password_hash(user.password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (user.username, user.email, hashed_password),
            )
            conn.commit()
    finally:
        conn.close()


def authenticate_user(user: UserLogin) -> str:
    """Weryfikuje dane, tworzy sesję i zwraca session_id."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, password_hash FROM users WHERE email = %s", (user.email,)
            )
            db_user = cursor.fetchone()

            if not db_user or not verify_password(
                user.password, db_user["password_hash"]
            ):
                raise HTTPException(
                    status_code=401, detail="Nieprawidłowy email lub hasło"
                )

            session_id = generate_session_id()
            expires_at = get_session_expiration()

            cursor.execute(
                "INSERT INTO sessions (session_id, user_id, expires_at) VALUES (%s, %s, %s)",
                (session_id, db_user["id"], expires_at),
            )
            conn.commit()
            return session_id
    finally:
        conn.close()


def remove_session(session_id: str) -> None:
    """Usuwa sesję z bazy danych."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM sessions WHERE session_id = %s", (session_id,))
            conn.commit()
    finally:
        conn.close()


def get_user_by_session(session_id: str) -> dict | None:
    """Pobiera dane użytkownika na podstawie ID sesji (dla dependencies)."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT u.id, u.username, u.email
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_id = %s AND s.expires_at > CURRENT_TIMESTAMP
            """,
                (session_id,),
            )
            return cursor.fetchone()
    finally:
        conn.close()
