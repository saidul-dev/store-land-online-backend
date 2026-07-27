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
