from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from . import crud, schemas
import requests
from database import get_db

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)
@router.post("/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=product)

@router.get("/", response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_products(db, skip=skip, limit=limit)

@router.get("/{product_id}", response_model=schemas.ProductResponse)
def read_product(product_id: UUID, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Produkt nie znaleziony")
    return db_product

@router.patch("/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: UUID, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    db_product = crud.update_product(db, product_id, product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Produkt nie znaleziony")
    return db_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: UUID, db: Session = Depends(get_db)):
    db_product = crud.delete_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Produkt nie znaleziony")
    return None

@router.post("/import/{barcode}", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def import_product_from_off(barcode: str, db: Session = Depends(get_db)):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"


    headers = {
        "User-Agent": "MójProjektBazyDanych/1.0 (studia-test)"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200 or response.json().get("status") != 1:
        raise HTTPException(status_code=404,
                            detail=f"Błąd API. Status: {response.status_code}, OFF nie znalazło kodu: {barcode}")

    data = response.json().get("product", {})
    nutriments = data.get("nutriments", {})

    new_product_data = schemas.ProductCreate(
        name=data.get("product_name", "Nieznany produkt z OFF"),
        quantity=100.0,
        quantity_unit="g",
        fat=float(nutriments.get("fat_100g") or 0.0),
        saturated_fat=float(nutriments.get("saturated-fat_100g") or 0.0),
        carbohydrates=float(nutriments.get("carbohydrates_100g") or 0.0),
        sugars=float(nutriments.get("sugars_100g") or 0.0),
        fiber=float(nutriments.get("fiber_100g") or 0.0),
        protein=float(nutriments.get("proteins_100g") or 0.0),
        salt=float(nutriments.get("salt_100g") or 0.0),
        energy_kcal=float(nutriments.get("energy-kcal_100g") or 0.0)
    )

    return crud.create_product(db=db, product=new_product_data)