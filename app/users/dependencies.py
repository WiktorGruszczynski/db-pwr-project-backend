from fastapi import Request, HTTPException, status
from app.database import get_db_connection
from datetime import datetime


def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Brak dostępu. Zaloguj się.",
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # szukamy sesji w bazie i wyciągamy dane użytkownika JOIN'em
        cursor.execute(
            """
            SELECT u.id, u.username, u.email 
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_id = %s AND s.expires_at > %s
        """,
            (session_id, datetime.now()),
        )

        user = cursor.fetchone()

        # jeśli sesji nie ma lub czas minął (expires_at)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesja wygasła lub jest nieprawidłowa.",
            )

        return user
    finally:
        cursor.close()
        conn.close()
