from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, Literal


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    quantity: float = Field(..., gt=0)
    quantity_unit: Literal["g"] = Field("g", description="Dozwolone tylko gramy (g)")
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
    quantity_unit: Optional[Literal["g"]] = None
    fat: Optional[float] = Field(None, ge=0)
    saturated_fat: Optional[float] = Field(None, ge=0)
    carbohydrates: Optional[float] = Field(None, ge=0)
    sugars: Optional[float] = Field(None, ge=0)
    fiber: Optional[float] = Field(None, ge=0)
    protein: Optional[float] = Field(None, ge=0)
    salt: Optional[float] = Field(None, ge=0)
    energy_kcal: Optional[float] = Field(None, ge=0)


class ProductResponse(ProductBase):
    id: UUID

    class Config:
        from_attributes = True
