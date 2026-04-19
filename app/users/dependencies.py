from fastapi import Request, HTTPException, status
from app.users.service import get_user_by_session


def get_current_user(request: Request) -> dict:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Brak sesji",
        )

    # delegujemy zapytanie do bazy do funkcji w serwisie
    user = get_user_by_session(session_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesja wygasła lub jest nieprawidłowa",
        )

    return user
