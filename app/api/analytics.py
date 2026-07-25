from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.core.rbac import require_permission
from app.crud.analytics import get_summary
from app.db.session import get_db
from app.models.store_membership import StoreMembership
from app.schemas.analytics import AnalyticsSummary

router = APIRouter(prefix="/stores/{store_id}/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary(
    store_id: int,
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    _membership: StoreMembership = Depends(require_permission(Permission.ORDERS_VIEW)),
):
    return get_summary(db, store_id, days=days)
