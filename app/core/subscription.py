from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.crud.membership import membership as membership_crud
from app.crud.product import product as product_crud
from app.crud.subscription import subscription as subscription_crud
from app.models.subscription import Subscription


def is_expired(subscription: Subscription) -> bool:
    if subscription.status in ("expired", "cancelled"):
        return True
    period_end = subscription.current_period_end
    if period_end is None:
        return False
    # SQLite (used in tests) drops tzinfo on round-trip even though the value
    # was always written as UTC — normalize so the comparison never raises.
    if period_end.tzinfo is None:
        period_end = period_end.replace(tzinfo=timezone.utc)
    return period_end < datetime.now(timezone.utc)


def check_subscription_active(db: Session, store_id: int) -> None:
    """Block mutating actions once a store's trial/plan period has lapsed.

    Read access (require_permission on a *_VIEW permission) never calls this —
    only the *_EDIT / *_MANAGE checks in require_permission do, so an expired
    store's admin panel stays browsable but read-only.
    """
    sub = subscription_crud.get_by_store(db, store_id)
    if sub is not None and is_expired(sub):
        raise HTTPException(
            status_code=402,
            detail="Your subscription has expired. Renew your plan to make changes.",
        )


def check_product_limit(db: Session, store_id: int) -> None:
    sub = subscription_crud.get_by_store(db, store_id)
    if sub is None or sub.plan.max_products is None:
        return
    if product_crud.count_by_store(db, store_id) >= sub.plan.max_products:
        raise HTTPException(
            status_code=400,
            detail=f"Product limit reached for the {sub.plan.name} plan ({sub.plan.max_products}). Upgrade to add more.",
        )


def check_staff_limit(db: Session, store_id: int) -> None:
    sub = subscription_crud.get_by_store(db, store_id)
    if sub is None or sub.plan.max_staff is None:
        return
    if len(membership_crud.get_by_store(db, store_id)) >= sub.plan.max_staff:
        raise HTTPException(
            status_code=400,
            detail=f"Staff limit reached for the {sub.plan.name} plan ({sub.plan.max_staff}). Upgrade to add more.",
        )
