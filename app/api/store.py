from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.core.rbac import require_permission
from app.core.security import get_current_user
from app.core.tenant import get_store_from_host
from app.crud.membership import membership as membership_crud
from app.crud.store import store as store_crud
from app.db.session import get_db
from app.models.store import Store
from app.models.store_membership import StoreMembership
from app.models.user import User
from app.schemas.store import StoreCreate, StoreRead, StoreSettingsUpdate

router = APIRouter(prefix="/stores", tags=["stores"])


@router.post("/", response_model=StoreRead, status_code=201)
def register_store(
    store_in: StoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if store_crud.get_by_subdomain(db, store_in.subdomain):
        raise HTTPException(status_code=400, detail="Subdomain already taken")
    new_store = store_crud.create(db, store_in, owner_id=current_user.id)
    membership_crud.add_member(db, store_id=new_store.id, user_id=current_user.id, role="owner")
    return new_store


@router.get("/me", response_model=list[StoreRead])
def list_my_stores(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return store_crud.get_by_owner(db, current_user.id)


@router.get("/resolve", response_model=StoreRead)
def resolve_store(store: Store = Depends(get_store_from_host)):
    """Resolve the store for the request's Host header (subdomain or verified custom domain).

    The frontend's tenant-routing middleware calls this to check whether a (sub)domain
    maps to a live store before rendering its storefront.
    """
    return store


@router.patch("/{store_id}/settings", response_model=StoreRead)
def update_store_settings(
    store_id: int,
    payload: StoreSettingsUpdate,
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.STORE_SETTINGS_EDIT)),
):
    db_store = store_crud.get(db, store_id)
    if db_store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return store_crud.update(db, db_store, payload)
