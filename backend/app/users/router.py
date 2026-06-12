from uuid import UUID
from typing import List
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from app.users.schemas import (
    UserRegister,
    UserLogin,
    UserVerify2FA,
    PasswordResetRequest,
    PasswordResetConfirm,
    FollowedUser,
    UserSearchResult,
)
from app.users.service import (
    register_new_user,
    verify_user_registration,
    authenticate_user,
    remove_session,
    send_password_reset_code,
    verify_and_reset_password,
    follow_user,
    unfollow_user,
    list_followed_users,
    search_users_by_username,
    get_user_public,
)
from app.users.dependencies import get_current_user
from app.database import get_db
from app.recipes import service as recipes_service
from app.recipes.schemas import RecipeListItem


auth_router = APIRouter(prefix="/auth", tags=["Auth"])
users_router = APIRouter(prefix="/users", tags=["Users"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, background_tasks: BackgroundTasks, db=Depends(get_db)):
    register_new_user(user, db, background_tasks)
    return {"message": "Konto utworzone. Sprawdź e-mail, aby aktywować konto."}


@auth_router.post("/verify", status_code=status.HTTP_200_OK)
def verify_email(data: UserVerify2FA, db=Depends(get_db)):
    verify_user_registration(data, db)
    return {
        "message": "Adres e-mail został pomyślnie zweryfikowany. Możesz się zalogować."
    }


@auth_router.post("/login")
def login(user: UserLogin, response: Response, db=Depends(get_db)):
    session_id = authenticate_user(user, db)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite="lax",
    )
    return {"message": "Zalogowano pomyślnie"}


@auth_router.post("/logout")
def logout(request: Request, response: Response, db=Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if session_id:
        remove_session(session_id, db)
    response.delete_cookie("session_id")
    return {"message": "Wylogowano"}


@auth_router.post("/forgot-password")
def forgot_password(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
):
    send_password_reset_code(request.email, db, background_tasks)
    return {
        "message": "Jeśli podany e-mail istnieje w bazie, wysłano na niego kod resetujący."
    }


@auth_router.post("/reset-password")
def reset_password(data: PasswordResetConfirm, db=Depends(get_db)):
    verify_and_reset_password(data.email, data.code, data.new_password, db)
    return {"message": "Hasło zostało pomyślnie zmienione. Możesz się teraz zalogować."}


@users_router.get("/me")
def get_my_profile(current_user: dict = Depends(get_current_user)):
    return {"message": "Witaj w tajnej strefie!", "user_data": current_user}


@users_router.get("/search", response_model=List[UserSearchResult])
def search_users(
    q: str = Query(
        ..., min_length=2, description="Fragment nazwy użytkownika (min. 2 znaki)"
    ),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    return search_users_by_username(q, db)


@users_router.get("/me/following", response_model=List[FollowedUser])
def list_following(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    return list_followed_users(str(current_user["id"]), db)


@users_router.post("/{followed_id}/follow", status_code=status.HTTP_201_CREATED)
def follow(
    followed_id: UUID,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    if str(current_user["id"]) == str(followed_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nie możesz obserwować samego siebie.",
        )
    follow_user(str(current_user["id"]), str(followed_id), db)
    return {"message": "Użytkownik zaobserwowany pomyślnie."}


@users_router.delete("/{followed_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow(
    followed_id: UUID,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    unfollow_user(str(current_user["id"]), str(followed_id), db)


@users_router.get("/{user_id}", response_model=UserSearchResult)
def get_public_profile(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """Publiczny profil uzytkownika (id + username)."""
    user = get_user_public(str(user_id), db)
    if not user:
        raise HTTPException(status_code=404, detail="Nie ma takiego użytkownika")
    return user


@users_router.get("/{user_id}/recipes", response_model=List[RecipeListItem])
def get_user_recipes(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """Przepisy utworzone przez wskazanego uzytkownika."""
    if not get_user_public(str(user_id), db):
        raise HTTPException(status_code=404, detail="Nie ma takiego użytkownika")
    return recipes_service.list_recipes_by_user(db, str(user_id))
