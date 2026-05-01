from fastapi import APIRouter, status, Response, Request, Depends
from app.users.schemas import (
    UserRegister, 
    UserLogin, 
    UserVerify2FA, 
    PasswordResetRequest, 
    PasswordResetConfirm
)
from app.users.service import (
    register_new_user, 
    verify_user_registration, 
    authenticate_user, 
    remove_session,
    send_password_reset_code,
    verify_and_reset_password
)
from app.users.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister):
    register_new_user(user)
    return {"message": "Konto utworzone. Sprawdź e-mail, aby aktywować konto."}

@router.post("/verify", status_code=status.HTTP_200_OK)
def verify_email(data: UserVerify2FA):
    verify_user_registration(data)
    return {"message": "Adres e-mail został pomyślnie zweryfikowany. Możesz się zalogować."}

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

@router.post("/forgot-password")
def forgot_password(request: PasswordResetRequest):
    send_password_reset_code(request.email)
    return {"message": "Jeśli podany e-mail istnieje w bazie, wysłano na niego kod resetujący."}

@router.post("/reset-password")
def reset_password(data: PasswordResetConfirm):
    verify_and_reset_password(data.email, data.code, data.new_password)
    return {"message": "Hasło zostało pomyślnie zmienione. Możesz się teraz zalogować."}