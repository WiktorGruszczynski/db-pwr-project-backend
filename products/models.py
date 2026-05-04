from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime


@dataclass
class Product:
    name: str
    quantity: float
    quantity_unit: str
    id: UUID = field(default_factory=uuid4)
    fat: float = 0.0
    saturated_fat: float = 0.0
    carbohydrates: float = 0.0
    sugars: float = 0.0
    fiber: float = 0.0
    protein: float = 0.0
    salt: float = 0.0
    energy_kcal: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
