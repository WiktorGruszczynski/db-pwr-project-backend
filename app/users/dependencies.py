from fastapi import Request, HTTPException, status, Depends
from app.users.service import get_user_by_session
from app.database import get_db


def get_current_user(request: Request, db=Depends(get_db)) -> dict:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Brak sesji",
        )

    # delegujemy zapytanie do bazy do funkcji w serwisie
    user = get_user_by_session(session_id, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesja wygasła lub jest nieprawidłowa",
        )

    return user
