from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.core.rbac import require_permission
from app.crud.product import product as product_crud
from app.crud.store import store as store_crud
from app.db.session import get_db
from app.models.store_membership import StoreMembership
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/stores/{store_id}/products", tags=["products"])


@router.get("/", response_model=list[ProductRead])
def list_products(store_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if store_crud.get(db, store_id) is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return product_crud.get_by_store(db, store_id, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(store_id: int, product_id: int, db: Session = Depends(get_db)):
    product = product_crud.get_by_store_and_id(db, store_id, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductRead, status_code=201)
def create_product(
    store_id: int,
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PRODUCTS_EDIT)),
):
    if product_crud.get_by_sku(db, store_id, payload.sku):
        raise HTTPException(status_code=400, detail="SKU already exists in this store")
    return product_crud.create(db, payload, store_id=store_id)


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    store_id: int,
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PRODUCTS_EDIT)),
):
    product = product_crud.get_by_store_and_id(db, store_id, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_crud.update(db, product, payload)


@router.delete("/{product_id}", status_code=204)
def delete_product(
    store_id: int,
    product_id: int,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PRODUCTS_EDIT)),
):
    product = product_crud.get_by_store_and_id(db, store_id, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    product_crud.remove(db, product)
