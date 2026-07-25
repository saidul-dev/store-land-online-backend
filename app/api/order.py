from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.permissions import ROLE_PERMISSIONS, Permission
from app.core.rbac import require_permission
from app.core.security import get_current_user
from app.crud.membership import membership as membership_crud
from app.crud.order import InsufficientStockError, VariantNotFoundError
from app.crud.order import order as order_crud
from app.crud.store import store as store_crud
from app.db.session import get_db
from app.models.store_membership import StoreMembership
from app.models.user import User
from app.schemas.order import OrderCreate, OrderRead, OrderStatusUpdate

router = APIRouter(prefix="/stores/{store_id}/orders", tags=["orders"])


@router.post("/", response_model=OrderRead, status_code=201)
def create_order(
    store_id: int,
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if store_crud.get(db, store_id) is None:
        raise HTTPException(status_code=404, detail="Store not found")
    try:
        return order_crud.create_with_items(
            db, store_id=store_id, customer_id=current_user.id, items_in=payload.items
        )
    except VariantNotFoundError as exc:
        raise HTTPException(
            status_code=404, detail=f"Variant {exc.variant_id} not found in this store"
        ) from exc
    except InsufficientStockError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock for SKU '{exc.sku}' (available: {exc.available})",
        ) from exc


@router.get("/mine", response_model=list[OrderRead])
def list_my_orders(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return order_crud.get_by_customer(db, store_id, current_user.id)


@router.get("/", response_model=list[OrderRead])
def list_orders(
    store_id: int,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.ORDERS_VIEW)),
):
    return order_crud.get_by_store(db, store_id)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    store_id: int,
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_order = order_crud.get_by_store_and_id(db, store_id, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if db_order.customer_id != current_user.id:
        membership = membership_crud.get_by_store_and_user(db, store_id, current_user.id)
        allowed = membership and Permission.ORDERS_VIEW in ROLE_PERMISSIONS.get(membership.role, set())
        if not allowed:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    return db_order


@router.patch("/{order_id}", response_model=OrderRead)
def update_order_status(
    store_id: int,
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.ORDERS_MANAGE)),
):
    db_order = order_crud.get_by_store_and_id(db, store_id, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    db_order.status = payload.status
    db.commit()
    db.refresh(db_order)
    return db_order
