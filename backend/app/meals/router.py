from typing import List
from uuid import UUID
from datetime import date as DateType
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.meals import service
from app.meals.schemas import MealItemCreate, MealItemResponse, MealResponse
from app.database import get_db
from app.users.dependencies import get_current_user


router = APIRouter(prefix="/meals", tags=["Meals"])


@router.get("/", response_model=List[MealResponse])
def list_meals(
    date: DateType = Query(..., description="Dzien w formacie YYYY-MM-DD"),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    return service.list_meals_for_day(db, str(current_user["id"]), date)


@router.post(
    "/items",
    response_model=MealItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_meal_item(
    data: MealItemCreate,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    return service.add_meal_item(db, str(current_user["id"]), data)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal_item(
    item_id: UUID,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    if not service.delete_meal_item(db, str(current_user["id"]), item_id):
        raise HTTPException(status_code=404, detail="Nie ma takiej pozycji")
