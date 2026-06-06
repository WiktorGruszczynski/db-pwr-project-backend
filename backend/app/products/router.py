from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from uuid import UUID
from typing import List
from app.products import service
from .schemas import ProductCreate, ProductUpdate, ProductResponse
from app.database import get_db
from app.users.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Utwórz nowy produkt",
    description="Dodaje nowy produkt do bazy danych. Domyślnie produkt jest oznaczony jako prywatny (`is_global=False`) i widoczny tylko dla jego twórcy.",
)
def create_product(
    product: ProductCreate,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return service.create_product(db, product, current_user["id"])


@router.get(
    "/search",
    response_model=List[ProductResponse],
    summary="Wyszukaj globalne produkty",
    description="Przeszukuje bazę produktów ogólnodostępnych (`is_global=True`) po fragmencie nazwy.",
)
def search_products(
    q: str = Query(..., min_length=3, description="Fragment nazwy (min. 3 znaki)"),
    db=Depends(get_db),
):
    return service.search_global_products(db, q)


@router.get(
    "/mine",
    response_model=List[ProductResponse],
    summary="Pobierz moje produkty",
    description="Zwraca listę wszystkich prywatnych produktów utworzonych przez zalogowanego użytkownika.",
)
def list_my_products(
    db=Depends(get_db), current_user: dict = Depends(get_current_user)
):
    return service.list_user_products(db, current_user["id"])


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Pobierz szczegóły produktu",
    description="Zwraca szczegółowe dane o makroskładnikach wskazanego produktu po jego ID.",
)
def get_product(product_id: UUID, db=Depends(get_db)):
    product = service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Nie ma takiego produktu")
    return product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Usuń produkt",
    description="Usuwa produkt z bazy danych. Uwaga: Usunięcie jest zablokowane, jeśli dany produkt jest wykorzystywany jako składnik w jakimkolwiek przepisie (ochrona RESTRICT).",
)
def delete_product(product_id: UUID, db=Depends(get_db)):
    if not service.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Nie znaleziono do usunięcia")


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Aktualizuj produkt",
    description="Pozwala na zmianę danych i wartości odżywczych produktu. Zmiany te automatycznie przeliczą kaloryczność powiązanych z nim przepisów.",
)
def update_product(product_id: str, product_update: ProductUpdate, db=Depends(get_db)):
    updated = service.patch_product(db, product_id, product_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found or no data sent")
    return updated


@router.patch(
    "/{product_id}/global",
    response_model=ProductResponse,
    summary="Zmień widoczność globalną produktu (Tylko ADMIN)",
    description="Pozwala przypisać lub odebrać produktowi status ogólnodostępnego w wyszukiwarce. Zabezpieczone zależnością `require_admin`.",
)
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
