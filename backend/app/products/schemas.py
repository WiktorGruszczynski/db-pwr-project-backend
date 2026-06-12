from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import Optional, Literal

from app.schemas import RoundedFloat


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(..., gt=0)
    quantity_unit: Literal["g"] = Field("g", description="Dozwolone tylko gramy (g)")
    fat: float = Field(0.0, ge=0)
    carbohydrates: float = Field(0.0, ge=0)
    protein: float = Field(0.0, ge=0)
    energy_kcal: float = Field(0.0, ge=0)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    quantity: Optional[float] = Field(None, gt=0)
    quantity_unit: Optional[Literal["g"]] = Field(
        None, description="Dozwolone tylko gramy (g)"
    )
    fat: Optional[float] = Field(None, ge=0)
    carbohydrates: Optional[float] = Field(None, ge=0)
    protein: Optional[float] = Field(None, ge=0)
    energy_kcal: Optional[float] = Field(None, ge=0)


class ProductResponse(BaseModel):
    id: UUID
    name: str
    quantity: RoundedFloat
    quantity_unit: str
    fat: RoundedFloat
    carbohydrates: RoundedFloat
    protein: RoundedFloat
    energy_kcal: RoundedFloat
    is_global: bool = False
    recipe_id: Optional[UUID] = Field(
        None, description="ID przepisu, z którego powstał auto-produkt"
    )

    model_config = ConfigDict(from_attributes=True)
