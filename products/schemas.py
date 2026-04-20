from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class ProductBase(BaseModel):
    name: str = Field(..., max_length=128, description="Nazwa produktu")
    quantity: float = Field(..., gt=0, description="Ilość musi być większa niż 0")
    quantity_unit: str = Field(..., max_length=8)
    fat: float = Field(0.0, ge=0)
    saturated_fat: float = Field(0.0, ge=0)
    carbohydrates: float = Field(0.0, ge=0)
    sugars: float = Field(0.0, ge=0)
    fiber: float = Field(0.0, ge=0)
    protein: float = Field(0.0, ge=0)
    salt: float = Field(0.0, ge=0)
    energy_kcal: float = Field(0.0, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=128)
    quantity: Optional[float] = Field(None, gt=0)
    energy_kcal: Optional[float] = Field(None, ge=0)


class ProductResponse(ProductBase):
    id: UUID

    class Config:
        from_attributes = True
