from fastapi import Request, Depends, HTTPException, status
from app.database import get_db
from app.users.service import get_user_by_session


def get_current_user(request: Request, db=Depends(get_db)):
    # wyciągamy ciastko
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Brak sesji. Zaloguj się ponownie.",
        )

    # szukamy użytkownika w bazie
    user = get_user_by_session(session_id, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowa lub wygasła sesja. Zaloguj się ponownie.",
        )

    return user
