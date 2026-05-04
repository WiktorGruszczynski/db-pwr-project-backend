from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
import service, schemas
from database import get_db

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db = Depends(get_db)):
    return service.create_product(db, product)

@router.get("/", response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db = Depends(get_db)):
    return service.get_products(db, skip, limit)

@router.get("/{product_id}", response_model=schemas.ProductResponse)
def read_product(product_id: UUID, db = Depends(get_db)):
    product = service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Nie ma takiego produktu")
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: UUID, db = Depends(get_db)):
    if not service.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Nie znaleziono do usunięcia")

# @router.post("/import/{barcode}", response_model=schemas.ProductResponse)
# def import_product(barcode: str, db = Depends(get_db)):
#     product = service.import_from_off(db, barcode)
#     if not product:
#         raise HTTPException(status_code=404, detail="OFF nie zna tego kodu")
#     return product

@router.patch("/{product_id}", response_model=schemas.ProductResponse)
def update_product_partial(
    product_id: str,
    product_update: schemas.ProductUpdate,
    db=Depends(get_db)
):
    updated = service.patch_product(db, product_id, product_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found or no data sent")
    return updated