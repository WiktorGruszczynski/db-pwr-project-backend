from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import Optional, List, Literal
from datetime import datetime

from app.schemas import RoundedFloat


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
    product_name: Optional[str] = None
    quantity: RoundedFloat
    unit: str

    model_config = ConfigDict(from_attributes=True)


class RecipeListItem(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    average_rating: Optional[RoundedFloat] = 0.0
    user_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class RecipeResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    average_rating: Optional[RoundedFloat] = 0.0
    my_rating: Optional[int] = Field(
        None, description="Ocena wystawiona przez aktualnego użytkownika (1-5)"
    )
    created_at: datetime
    user_id: UUID
    ingredients: List[IngredientOut] = []
    product_id: Optional[UUID] = Field(
        None, description="ID auto-utworzonego produktu z tego przepisu"
    )
    is_private: bool = Field(
        True,
        description="True, gdy auto-produkt przepisu nie jest globalny "
        "(widzi go tylko autor)",
    )

    model_config = ConfigDict(from_attributes=True)


class RatingIn(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Ocena w skali 1-5")


class RatingResponse(BaseModel):
    average_rating: RoundedFloat
    my_rating: int
