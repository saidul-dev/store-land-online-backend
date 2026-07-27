from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.permissions import ROLE_PERMISSIONS, Permission
from app.core.security import get_current_user
from app.core.subscription import check_subscription_active
from app.crud.membership import membership as membership_crud
from app.db.session import get_db
from app.models.store_membership import StoreMembership
from app.models.user import User


def get_current_membership(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StoreMembership:
    """Resolve the caller's membership in the store identified by the `store_id` path param.

    404s rather than 403s when there is no membership, so staff can't probe which
    store IDs exist by comparing 403 vs 404 responses.
    """
    membership = membership_crud.get_by_store_and_user(db, store_id, current_user.id)
    if membership is None:
        raise HTTPException(status_code=404, detail="Store not found or you are not a member")
    return membership


def require_permission(permission: Permission):
    def checker(
        membership: StoreMembership = Depends(get_current_membership),
        db: Session = Depends(get_db),
    ) -> StoreMembership:
        if permission not in ROLE_PERMISSIONS.get(membership.role, set()):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        # "*.view" permissions stay readable even with a lapsed subscription —
        # only mutating permissions (*.edit / *.manage) are gated.
        if not permission.value.endswith(".view"):
            check_subscription_active(db, membership.store_id)
        return membership

    return checker
