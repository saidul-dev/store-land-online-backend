from datetime import datetime

from pydantic import BaseModel

from app.schemas.plan import PlanRead


class SubscriptionRead(BaseModel):
    id: int
    store_id: int
    status: str
    current_period_end: datetime | None
    plan: PlanRead

    class Config:
        from_attributes = True


class SubscriptionSummary(BaseModel):
    subscription: SubscriptionRead
    is_expired: bool
    products_used: int
    staff_used: int
