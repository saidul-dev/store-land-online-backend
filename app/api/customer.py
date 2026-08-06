from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.core.rbac import require_permission
from app.crud.customer import customer as customer_crud
from app.db.session import get_db
from app.models.store_membership import StoreMembership
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate

router = APIRouter(prefix="/stores/{store_id}/customers", tags=["customers"])


@router.get("/", response_model=list[CustomerRead])
def list_customers(
    store_id: int,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.CUSTOMERS_VIEW)),
):
    return customer_crud.get_by_store(db, store_id)


@router.post("/", response_model=CustomerRead, status_code=201)
def create_customer(
    store_id: int,
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.CUSTOMERS_MANAGE)),
):
    return customer_crud.create(db, payload, store_id=store_id)


@router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(
    store_id: int,
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.CUSTOMERS_MANAGE)),
):
    db_customer = customer_crud.get_by_store_and_id(db, store_id, customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer_crud.update(db, db_customer, payload)


@router.delete("/{customer_id}", status_code=204)
def delete_customer(
    store_id: int,
    customer_id: int,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.CUSTOMERS_MANAGE)),
):
    db_customer = customer_crud.get_by_store_and_id(db, store_id, customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer_crud.remove(db, db_customer)
