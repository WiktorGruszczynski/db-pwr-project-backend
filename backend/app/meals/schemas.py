from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import date as DateType
from typing import Literal, List

from app.schemas import RoundedFloat


MealType = Literal["BREAKFAST", "LUNCH", "DINNER", "SNACK"]


class MealItemCreate(BaseModel):
    date: DateType
    meal_type: MealType
    product_id: UUID
    portion: float = Field(..., gt=0, description="Wielkosc porcji w gramach")


class MealItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    product_name: str
    portion: RoundedFloat
    fat: RoundedFloat
    carbohydrates: RoundedFloat
    protein: RoundedFloat
    energy_kcal: RoundedFloat

    model_config = ConfigDict(from_attributes=True)


class MealResponse(BaseModel):
    id: UUID
    date: DateType
    meal_type: MealType
    items: List[MealItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
