from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from uuid import UUID
from typing import List
from app.products import service
from .schemas import ProductCreate, ProductUpdate, ProductResponse
from app.database import get_db
from app.users.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return service.create_product(db, product, current_user["id"])


@router.get("/search", response_model=List[ProductResponse])
def search_products(
    q: str = Query(..., min_length=3, description="Fragment nazwy (min. 3 znaki)"),
    db=Depends(get_db),
):
    return service.search_global_products(db, q)


@router.get("/mine", response_model=List[ProductResponse])
def list_my_products(
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return service.list_user_products(db, current_user["id"])


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: UUID, db=Depends(get_db)):
    product = service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Nie ma takiego produktu")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: UUID, db=Depends(get_db)):
    if not service.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Nie znaleziono do usunięcia")


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: str, product_update: ProductUpdate, db=Depends(get_db)):
    updated = service.patch_product(db, product_id, product_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found or no data sent")
    return updated


@router.patch("/{product_id}/global", response_model=ProductResponse)
def set_global(
    product_id: UUID,
    is_global: bool = Body(..., embed=True),
    db=Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Tylko ADMIN — ustawia lub zdejmuje flagę is_global na produkcie."""
    updated = service.set_product_global(db, product_id, is_global)
    if not updated:
        raise HTTPException(status_code=404, detail="Nie ma takiego produktu")
    return updated
