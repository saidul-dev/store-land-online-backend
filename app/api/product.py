from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.core.rbac import require_permission
from app.core.subscription import check_product_limit
from app.crud.product import DuplicateSKUError
from app.crud.product import product as product_crud
from app.crud.product import variant as variant_crud
from app.crud.store import store as store_crud
from app.db.session import get_db
from app.models.store_membership import StoreMembership
from app.schemas.common import Page
from app.schemas.product import (
    ProductCreate,
    ProductRead,
    ProductUpdate,
    ProductVariantCreate,
    ProductVariantRead,
    ProductVariantUpdate,
)

router = APIRouter(prefix="/stores/{store_id}/products", tags=["products"])


@router.get("/", response_model=Page[ProductRead])
def list_products(
    store_id: int,
    category_id: int | None = None,
    brand_id: int | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if store_crud.get(db, store_id) is None:
        raise HTTPException(status_code=404, detail="Store not found")
    skip = (page - 1) * limit
    items = product_crud.get_by_store(db, store_id, category_id=category_id, brand_id=brand_id, skip=skip, limit=limit)
    total = product_crud.count_by_store(db, store_id, category_id=category_id, brand_id=brand_id)
    return Page(items=items, total=total, page=page, limit=limit)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(store_id: int, product_id: int, db: Session = Depends(get_db)):
    db_product = product_crud.get_by_store_and_id(db, store_id, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.post("/", response_model=ProductRead, status_code=201)
def create_product(
    store_id: int,
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PRODUCTS_EDIT)),
):
    check_product_limit(db, store_id)
    try:
        return product_crud.create_with_variants(db, store_id=store_id, payload=payload)
    except DuplicateSKUError as exc:
        raise HTTPException(status_code=400, detail=f"SKU '{exc.sku}' already exists in this store") from exc


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    store_id: int,
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PRODUCTS_EDIT)),
):
    db_product = product_crud.get_by_store_and_id(db, store_id, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_crud.update(db, db_product, payload)


@router.delete("/{product_id}", status_code=204)
def delete_product(
    store_id: int,
    product_id: int,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PRODUCTS_EDIT)),
):
    db_product = product_crud.get_by_store_and_id(db, store_id, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    product_crud.remove(db, db_product)


@router.post("/{product_id}/variants", response_model=ProductVariantRead, status_code=201)
def add_variant(
    store_id: int,
    product_id: int,
    payload: ProductVariantCreate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PRODUCTS_EDIT)),
):
    db_product = product_crud.get_by_store_and_id(db, store_id, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        return product_crud.add_variant(db, store_id=store_id, product=db_product, variant_in=payload)
    except DuplicateSKUError as exc:
        raise HTTPException(status_code=400, detail=f"SKU '{exc.sku}' already exists in this store") from exc


@router.put("/{product_id}/variants/{variant_id}", response_model=ProductVariantRead)
def update_variant(
    store_id: int,
    product_id: int,
    variant_id: int,
    payload: ProductVariantUpdate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PRODUCTS_EDIT)),
):
    db_variant = product_crud.get_variant(db, store_id, product_id, variant_id)
    if db_variant is None:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant_crud.update(db, db_variant, payload)


@router.delete("/{product_id}/variants/{variant_id}", status_code=204)
def delete_variant(
    store_id: int,
    product_id: int,
    variant_id: int,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PRODUCTS_EDIT)),
):
    db_variant = product_crud.get_variant(db, store_id, product_id, variant_id)
    if db_variant is None:
        raise HTTPException(status_code=404, detail="Variant not found")
    variant_crud.remove(db, db_variant)
