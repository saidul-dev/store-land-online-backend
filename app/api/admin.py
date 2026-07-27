from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.rbac import require_super_admin
from app.crud.plan import plan as plan_crud
from app.crud.subscription import subscription as subscription_crud
from app.db.session import get_db
from app.models.store import Store
from app.models.user import User
from app.schemas.admin import AdminStoreRead, UpdateStoreSubscription
from app.schemas.plan import PlanRead
from app.schemas.subscription import SubscriptionRead

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stores", response_model=list[AdminStoreRead])
def list_all_stores(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    stores = db.query(Store).all()
    return [
        AdminStoreRead(
            id=store.id,
            name=store.name,
            subdomain=store.subdomain,
            owner_email=store.owner.email,
            created_at=store.created_at,
            subscription=(
                SubscriptionRead.model_validate(sub)
                if (sub := subscription_crud.get_by_store(db, store.id))
                else None
            ),
        )
        for store in stores
    ]


@router.get("/plans", response_model=list[PlanRead])
def list_all_plans(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    return plan_crud.get_multi(db, limit=1000)


@router.patch("/stores/{store_id}/subscription", response_model=SubscriptionRead)
def update_store_subscription(
    store_id: int,
    payload: UpdateStoreSubscription,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    sub = subscription_crud.get_by_store(db, store_id)
    if sub is None:
        raise HTTPException(status_code=404, detail="Store has no subscription record")
    target_plan = plan_crud.get(db, payload.plan_id)
    if target_plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    sub.plan_id = payload.plan_id
    sub.status = payload.status
    sub.current_period_end = payload.current_period_end
    db.commit()
    db.refresh(sub)
    return sub
