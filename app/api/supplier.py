from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.core.rbac import require_permission
from app.crud.supplier import supplier as supplier_crud
from app.db.session import get_db
from app.models.store_membership import StoreMembership
from app.schemas.supplier import SupplierCreate, SupplierRead, SupplierUpdate

router = APIRouter(prefix="/stores/{store_id}/suppliers", tags=["suppliers"])


@router.get("/", response_model=list[SupplierRead])
def list_suppliers(
    store_id: int,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PURCHASES_VIEW)),
):
    return supplier_crud.get_by_store(db, store_id)


@router.post("/", response_model=SupplierRead, status_code=201)
def create_supplier(
    store_id: int,
    payload: SupplierCreate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PURCHASES_MANAGE)),
):
    return supplier_crud.create(db, payload, store_id=store_id)


@router.put("/{supplier_id}", response_model=SupplierRead)
def update_supplier(
    store_id: int,
    supplier_id: int,
    payload: SupplierUpdate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PURCHASES_MANAGE)),
):
    db_supplier = supplier_crud.get_by_store_and_id(db, store_id, supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier_crud.update(db, db_supplier, payload)


@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(
    store_id: int,
    supplier_id: int,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.PURCHASES_MANAGE)),
):
    db_supplier = supplier_crud.get_by_store_and_id(db, store_id, supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    supplier_crud.remove(db, db_supplier)
