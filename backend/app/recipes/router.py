from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from app.recipes import service
from .schemas import (
    RatingIn,
    RatingResponse,
    RecipeCreate,
    RecipeListItem,
    RecipeResponse,
    RecipeUpdate,
)
from app.database import get_db
from app.users.dependencies import get_current_user

router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def create_recipe(
    recipe: RecipeCreate,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return service.create_recipe(db, recipe, current_user["id"])


@router.get("/search", response_model=List[RecipeListItem])
def search_recipes(
    q: str = Query(
        ..., min_length=2, description="Fragment nazwy przepisu (min. 2 znaki)"
    ),
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return service.search_recipes_by_name(db, q)


@router.get("/mine", response_model=List[RecipeListItem])
def list_my_recipes(
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Przepisy utworzone przez zalogowanego uzytkownika."""
    return service.list_recipes_by_user(db, current_user["id"])


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: UUID,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    recipe = service.get_recipe(db, recipe_id, current_user["id"])
    if not recipe:
        raise HTTPException(status_code=404, detail="Nie ma takiego przepisu")
    return recipe


@router.post("/{recipe_id}/rating", response_model=RatingResponse)
def rate_recipe(
    recipe_id: UUID,
    data: RatingIn,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = service.rate_recipe(db, recipe_id, current_user["id"], data.rating)
    if not result:
        raise HTTPException(status_code=404, detail="Nie ma takiego przepisu")
    return result


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: UUID,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not service.delete_recipe(db, recipe_id, current_user["id"]):
        raise HTTPException(status_code=404, detail="Nie ma takiego przepisu")


@router.patch("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: UUID,
    data: RecipeUpdate,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    updated = service.update_recipe(db, recipe_id, data, current_user["id"])
    if not updated:
        raise HTTPException(status_code=404, detail="Nie ma takiego przepisu")
    return updated
