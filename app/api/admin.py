from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.rbac import require_super_admin
from app.crud.membership import membership as membership_crud
from app.crud.plan import plan as plan_crud
from app.crud.site_content import site_content as site_content_crud
from app.crud.site_feature import site_feature as site_feature_crud
from app.crud.subscription import subscription as subscription_crud
from app.db.session import get_db
from app.models.store import Store
from app.models.user import User
from app.schemas.admin import AdminMembershipRead, AdminStoreRead, UpdateStoreSubscription
from app.schemas.plan import PlanCreate, PlanRead
from app.schemas.site_content import (
    SiteContentRead,
    SiteContentUpdate,
    SiteFeatureCreate,
    SiteFeatureRead,
    SiteFeatureUpdate,
)
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


@router.get("/staff", response_model=list[AdminMembershipRead])
def list_all_staff(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    memberships = membership_crud.get_all(db)
    return [
        AdminMembershipRead(
            id=m.id,
            store_id=m.store_id,
            store_name=m.store.name,
            store_subdomain=m.store.subdomain,
            user_id=m.user_id,
            user_email=m.user.email,
            user_name=m.user.name,
            role=m.role,
            created_at=m.created_at,
        )
        for m in memberships
    ]


@router.get("/plans", response_model=list[PlanRead])
def list_all_plans(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    return plan_crud.get_multi(db, limit=1000)


@router.post("/plans", response_model=PlanRead, status_code=201)
def create_plan(
    payload: PlanCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    if plan_crud.get_by_slug(db, payload.slug):
        raise HTTPException(status_code=400, detail="A plan with this slug already exists")
    return plan_crud.create(db, payload)


@router.get("/site-content/hero", response_model=SiteContentRead)
def get_site_hero(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    return site_content_crud.get(db)


@router.put("/site-content/hero", response_model=SiteContentRead)
def update_site_hero(
    payload: SiteContentUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    return site_content_crud.update(db, payload)


@router.get("/site-content/features", response_model=list[SiteFeatureRead])
def list_site_features(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    return site_feature_crud.get_all_ordered(db)


@router.post("/site-content/features", response_model=SiteFeatureRead, status_code=201)
def create_site_feature(
    payload: SiteFeatureCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    return site_feature_crud.create(db, payload)


@router.patch("/site-content/features/{feature_id}", response_model=SiteFeatureRead)
def update_site_feature(
    feature_id: int,
    payload: SiteFeatureUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    feature = site_feature_crud.get(db, feature_id)
    if feature is None:
        raise HTTPException(status_code=404, detail="Feature not found")
    return site_feature_crud.update(db, feature, payload)


@router.delete("/site-content/features/{feature_id}", status_code=204)
def delete_site_feature(
    feature_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    feature = site_feature_crud.get(db, feature_id)
    if feature is None:
        raise HTTPException(status_code=404, detail="Feature not found")
    site_feature_crud.remove(db, feature)


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
