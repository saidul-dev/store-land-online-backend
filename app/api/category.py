from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.core.rbac import require_permission
from app.crud.category import category as category_crud
from app.crud.store import store as store_crud
from app.db.session import get_db
from app.models.category import Category
from app.models.product import Product
from app.models.store_membership import StoreMembership
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/stores/{store_id}/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryRead])
def list_categories(store_id: int, db: Session = Depends(get_db)):
    if store_crud.get(db, store_id) is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return category_crud.get_by_store(db, store_id)


@router.post("/", response_model=CategoryRead, status_code=201)
def create_category(
    store_id: int,
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PRODUCTS_EDIT)),
):
    if category_crud.get_by_slug(db, store_id, payload.slug):
        raise HTTPException(status_code=400, detail="Slug already exists in this store")
    if payload.parent_id is not None and category_crud.get_by_store_and_id(db, store_id, payload.parent_id) is None:
        raise HTTPException(status_code=404, detail="Parent category not found")
    return category_crud.create(db, payload, store_id=store_id)


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    store_id: int,
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PRODUCTS_EDIT)),
):
    db_category = category_crud.get_by_store_and_id(db, store_id, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if payload.parent_id is not None and category_crud.get_by_store_and_id(db, store_id, payload.parent_id) is None:
        raise HTTPException(status_code=404, detail="Parent category not found")
    return category_crud.update(db, db_category, payload)


@router.delete("/{category_id}", status_code=204)
def delete_category(
    store_id: int,
    category_id: int,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PRODUCTS_EDIT)),
):
    db_category = category_crud.get_by_store_and_id(db, store_id, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    product_count = db.query(Product).filter(Product.category_id == category_id).count()
    if product_count:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete: {product_count} product(s) still use this category. Reassign or delete them first.",
        )
    child_count = db.query(Category).filter(Category.parent_id == category_id).count()
    if child_count:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete: {child_count} subcategory(ies) still have this as their parent.",
        )
    category_crud.remove(db, db_category)
