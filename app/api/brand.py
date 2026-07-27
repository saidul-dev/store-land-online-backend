from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.core.rbac import require_permission
from app.crud.brand import brand as brand_crud
from app.crud.store import store as store_crud
from app.db.session import get_db
from app.models.product import Product
from app.models.store_membership import StoreMembership
from app.schemas.brand import BrandCreate, BrandRead, BrandUpdate

router = APIRouter(prefix="/stores/{store_id}/brands", tags=["brands"])


@router.get("/", response_model=list[BrandRead])
def list_brands(store_id: int, db: Session = Depends(get_db)):
    if store_crud.get(db, store_id) is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return brand_crud.get_by_store(db, store_id)


@router.post("/", response_model=BrandRead, status_code=201)
def create_brand(
    store_id: int,
    payload: BrandCreate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PRODUCTS_EDIT)),
):
    if brand_crud.get_by_slug(db, store_id, payload.slug):
        raise HTTPException(status_code=400, detail="Slug already exists in this store")
    return brand_crud.create(db, payload, store_id=store_id)


@router.put("/{brand_id}", response_model=BrandRead)
def update_brand(
    store_id: int,
    brand_id: int,
    payload: BrandUpdate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PRODUCTS_EDIT)),
):
    db_brand = brand_crud.get_by_store_and_id(db, store_id, brand_id)
    if db_brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand_crud.update(db, db_brand, payload)


@router.delete("/{brand_id}", status_code=204)
def delete_brand(
    store_id: int,
    brand_id: int,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PRODUCTS_EDIT)),
):
    db_brand = brand_crud.get_by_store_and_id(db, store_id, brand_id)
    if db_brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")

    product_count = db.query(Product).filter(Product.brand_id == brand_id).count()
    if product_count:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete: {product_count} product(s) still use this brand. Reassign or delete them first.",
        )
    brand_crud.remove(db, db_brand)
