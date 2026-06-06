from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.recipes import service
from .schemas import RecipeCreate, RecipeUpdate, RecipeResponse
from app.database import get_db
from app.users.dependencies import get_current_user

router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.post(
    "/",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Utwórz nowy przepis",
    description="Zapisuje nowy przepis w bazie. Dodanie przepisu powoduje również automatyczne wygenerowanie 'wirtualnego produktu' w tabeli produktów, który przechowuje zsumowane makroskładniki na 100g.",
)
def create_recipe(
    recipe: RecipeCreate,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return service.create_recipe(db, recipe, current_user["id"])


@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Pobierz szczegóły przepisu",
    description="Zwraca wszystkie informacje o przepisie, w tym listę użytych w nim składników.",
)
def get_recipe(recipe_id: UUID, db=Depends(get_db)):
    recipe = service.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Nie ma takiego przepisu")
    return recipe


@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Usuń przepis",
    description="Całkowicie usuwa przepis z książki kucharskiej. Usunięcie kaskadowo wykasuje też powiązane z nim składniki i wirtualny produkt.",
)
def delete_recipe(
    recipe_id: UUID,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not service.delete_recipe(db, recipe_id, current_user["id"]):
        raise HTTPException(status_code=404, detail="Nie ma takiego przepisu")


@router.patch(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Aktualizuj przepis",
    description="Pozwala na modyfikację nazwy, opisu oraz składników przepisu. Wyzwala mechanizm przeliczania wartości odżywczych dla wirtualnego produktu.",
)
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
