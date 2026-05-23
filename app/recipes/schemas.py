from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import Optional, List, Literal
from datetime import datetime


class IngredientIn(BaseModel):
    product_id: UUID
    quantity: float = Field(..., gt=0)
    unit: Literal["g"] = Field("g", description="Dozwolone tylko gramy (g)")


class RecipeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    ingredients: List[IngredientIn] = Field(..., min_length=1)


class RecipeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    ingredients: Optional[List[IngredientIn]] = Field(None, min_length=1)


class IngredientOut(BaseModel):
    id: UUID
    product_id: UUID
    quantity: float
    unit: str

    model_config = ConfigDict(from_attributes=True)


class RecipeResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    average_rating: Optional[float] = 0.0
    created_at: datetime
    user_id: UUID
    ingredients: List[IngredientOut] = []
    product_id: Optional[UUID] = Field(
        None, description="ID auto-utworzonego produktu z tego przepisu"
    )

    model_config = ConfigDict(from_attributes=True)
