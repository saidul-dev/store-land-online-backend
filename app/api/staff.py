from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.core.rbac import require_permission
from app.core.subscription import check_staff_limit
from app.crud import user as user_crud
from app.crud.membership import membership as membership_crud
from app.db.session import get_db
from app.models.store_membership import StoreMembership
from app.schemas.membership import MembershipCreate, MembershipRead, MembershipRoleUpdate
from app.schemas.user import UserCreate

router = APIRouter(prefix="/stores/{store_id}/staff", tags=["staff"])


@router.get("/", response_model=list[MembershipRead])
def list_staff(
    store_id: int,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.STAFF_VIEW)),
):
    return membership_crud.get_by_store(db, store_id)


@router.post("/", response_model=MembershipRead, status_code=201)
def add_staff(
    store_id: int,
    payload: MembershipCreate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.STAFF_MANAGE)),
):
    target_user = user_crud.get_user_by_email(db, payload.email)
    if target_user is None:
        if not payload.password:
            raise HTTPException(status_code=404, detail="No registered user with that email")
        target_user = user_crud.create_user(
            db, UserCreate(email=payload.email, password=payload.password), name=payload.name
        )
    elif membership_crud.get_by_store_and_user(db, store_id, target_user.id):
        raise HTTPException(status_code=400, detail="User is already a member of this store")
    check_staff_limit(db, store_id)
    return membership_crud.add_member(db, store_id=store_id, user_id=target_user.id, role=payload.role)


@router.patch("/{membership_id}", response_model=MembershipRead)
def update_staff_role(
    store_id: int,
    membership_id: int,
    payload: MembershipRoleUpdate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.STAFF_MANAGE)),
):
    target = membership_crud.get(db, membership_id)
    if target is None or target.store_id != store_id:
        raise HTTPException(status_code=404, detail="Staff member not found")
    if target.role == "owner":
        raise HTTPException(status_code=400, detail="Cannot change the store owner's role")
    return membership_crud.update(db, target, payload)


@router.delete("/{membership_id}", status_code=204)
def remove_staff(
    store_id: int,
    membership_id: int,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.STAFF_MANAGE)),
):
    target = membership_crud.get(db, membership_id)
    if target is None or target.store_id != store_id:
        raise HTTPException(status_code=404, detail="Staff member not found")
    if target.role == "owner":
        raise HTTPException(status_code=400, detail="Cannot remove the store owner")
    membership_crud.remove(db, target)
