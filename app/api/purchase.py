from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.core.rbac import require_permission
from app.core.security import get_current_user
from app.crud.purchase import InvalidPurchaseStatusError, VariantNotFoundError
from app.crud.purchase import purchase as purchase_crud
from app.crud.supplier import supplier as supplier_crud
from app.db.session import get_db
from app.models.store_membership import StoreMembership
from app.models.user import User
from app.schemas.common import Page
from app.schemas.purchase import PurchaseCreate, PurchaseRead

router = APIRouter(prefix="/stores/{store_id}/purchases", tags=["purchases"])


@router.post("/", response_model=PurchaseRead, status_code=201)
def create_purchase(
    store_id: int,
    payload: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _membership: StoreMembership = Depends(require_permission(Permission.PURCHASES_MANAGE)),
):
    if supplier_crud.get_by_store_and_id(db, store_id, payload.supplier_id) is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    try:
        return purchase_crud.create_with_items(
            db, store_id=store_id, created_by_id=current_user.id, payload=payload
        )
    except VariantNotFoundError as exc:
        raise HTTPException(
            status_code=404, detail=f"Variant {exc.variant_id} not found in this store"
        ) from exc


@router.get("/", response_model=Page[PurchaseRead])
def list_purchases(
    store_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PURCHASES_VIEW)),
):
    skip = (page - 1) * limit
    items = purchase_crud.get_by_store(db, store_id, skip=skip, limit=limit)
    total = purchase_crud.count_by_store(db, store_id)
    return Page(items=items, total=total, page=page, limit=limit)


@router.get("/{purchase_id}", response_model=PurchaseRead)
def get_purchase(
    store_id: int,
    purchase_id: int,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PURCHASES_VIEW)),
):
    db_purchase = purchase_crud.get_by_store_and_id(db, store_id, purchase_id)
    if db_purchase is None:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return db_purchase


@router.post("/{purchase_id}/receive", response_model=PurchaseRead)
def receive_purchase(
    store_id: int,
    purchase_id: int,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PURCHASES_MANAGE)),
):
    db_purchase = purchase_crud.get_by_store_and_id(db, store_id, purchase_id)
    if db_purchase is None:
        raise HTTPException(status_code=404, detail="Purchase not found")
    try:
        return purchase_crud.receive(db, db_purchase)
    except InvalidPurchaseStatusError as exc:
        raise HTTPException(
            status_code=400, detail=f"Purchase is '{exc.current_status}', can only receive a pending purchase"
        ) from exc


@router.post("/{purchase_id}/cancel", response_model=PurchaseRead)
def cancel_purchase(
    store_id: int,
    purchase_id: int,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PURCHASES_MANAGE)),
):
    db_purchase = purchase_crud.get_by_store_and_id(db, store_id, purchase_id)
    if db_purchase is None:
        raise HTTPException(status_code=404, detail="Purchase not found")
    try:
        return purchase_crud.cancel(db, db_purchase)
    except InvalidPurchaseStatusError as exc:
        raise HTTPException(
            status_code=400, detail=f"Purchase is '{exc.current_status}', can only cancel a pending purchase"
        ) from exc
