from fastapi import APIRouter, HTTPException, status, Response, Request, Depends
from app.users.schemas import UserRegister, UserLogin
from app.users.service import (
    get_password_hash,
    verify_password,
    generate_session_id,
    get_session_expiration,
)
from app.users.dependencies import get_current_user
from app.database import get_db_connection

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
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
        return {"message": "Rejestracja zakończona sukcesem"}
    finally:
        cursor.close()
        conn.close()


@router.post("/login")
def login(user: UserLogin, response: Response):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, password_hash FROM users WHERE email = %s", (user.email,)
        )
        db_user = cursor.fetchone()

        if not db_user or not verify_password(user.password, db_user["password_hash"]):
            raise HTTPException(status_code=401, detail="Nieprawidłowy email lub hasło")

        session_id = generate_session_id()
        expires_at = get_session_expiration()

        cursor.execute(
            "INSERT INTO sessions (session_id, user_id, expires_at) VALUES (%s, %s, %s)",
            (session_id, db_user["id"], expires_at),
        )
        conn.commit()

        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            max_age=7 * 24 * 60 * 60,
            samesite="lax",
        )
        return {"message": "Zalogowano pomyślnie"}
    finally:
        cursor.close()
        conn.close()


@router.post("/logout")
def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM sessions WHERE session_id = %s", (session_id,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    response.delete_cookie("session_id")
    return {"message": "Wylogowano"}


@router.get("/me")
def get_my_profile(current_user: dict = Depends(get_current_user)):
    return {"message": "Witaj w tajnej strefie!", "user_data": current_user}
