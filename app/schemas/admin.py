from datetime import datetime

from pydantic import BaseModel

from app.schemas.subscription import SubscriptionRead


class AdminStoreRead(BaseModel):
    id: int
    name: str
    subdomain: str
    owner_email: str
    created_at: datetime
    subscription: SubscriptionRead | None = None


class UpdateStoreSubscription(BaseModel):
    plan_id: int
    status: str = "active"
    current_period_end: datetime | None = None


class AdminMembershipRead(BaseModel):
    id: int
    store_id: int
    store_name: str
    store_subdomain: str
    user_id: int
    user_email: str
    user_name: str | None
    role: str
    created_at: datetime
