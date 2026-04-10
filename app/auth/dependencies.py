from fastapi import Request, HTTPException, status
from app.database import get_db_connection
from datetime import datetime

def get_current_user(request: Request):
    # 1. Sprawdzamy, czy przeglądarka w ogóle przysłała ciastko
    session_id = request.cookies.get("session_id")
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Brak dostępu. Zaloguj się."
        )
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 2. Szukamy sesji w bazie i wyciągamy dane użytkownika za pomocą złączenia JOIN
        cursor.execute("""
            SELECT u.id, u.username, u.email 
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_id = %s AND s.expires_at > %s
        """, (session_id, datetime.now()))
        
        user = cursor.fetchone()
        
        # 3. Jeśli sesji nie ma lub czas minął (expires_at)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesja wygasła lub jest nieprawidłowa."
            )
            
        # 4. Zwracamy dane użytkownika, żeby endpoint wiedział, kto puka
        return user 
    finally:
        cursor.close()
        conn.close()