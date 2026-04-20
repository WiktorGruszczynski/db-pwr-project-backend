from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from database import Base


class Product(Base):
    __tablename__ = "products_product"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), nullable=False)
    quantity = Column(Float, nullable=False)
    quantity_unit = Column(String(8), nullable=False)

    fat = Column(Float, default=0.0)
    saturated_fat = Column(Float, default=0.0)
    carbohydrates = Column(Float, default=0.0)
    sugars = Column(Float, default=0.0)
    fiber = Column(Float, default=0.0)
    protein = Column(Float, default=0.0)
    salt = Column(Float, default=0.0)
    energy_kcal = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # TYMCZASOWO WYŁĄCZONE:
    # user_id = Column(UUID(as_uuid=True), ForeignKey("users_user.id"), nullable=False)
    # recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes_recipe.id"), nullable=True)
