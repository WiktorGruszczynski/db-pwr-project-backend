from fastapi import APIRouter, status, Response, Request, Depends
from app.users.schemas import UserRegister, UserLogin
from app.users.service import register_new_user, authenticate_user, remove_session
from app.users.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister):
    register_new_user(user)
    return {"message": "Rejestracja zakończona sukcesem"}


@router.post("/login")
def login(user: UserLogin, response: Response):
    session_id = authenticate_user(user)

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite="lax",
    )
    return {"message": "Zalogowano pomyślnie"}


@router.post("/logout")
def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id:
        remove_session(session_id)

    response.delete_cookie("session_id")
    return {"message": "Wylogowano"}


@router.get("/me")
def get_my_profile(current_user: dict = Depends(get_current_user)):
    return {"message": "Witaj w tajnej strefie!", "user_data": current_user}
