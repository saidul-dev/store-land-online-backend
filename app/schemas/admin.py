from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr

from app.schemas.subscription import SubscriptionRead


class AdminStoreRead(BaseModel):
    id: int
    name: str
    subdomain: str
    owner_email: str
    created_at: datetime
    subscription: SubscriptionRead | None = None
    usage_tier: str = "light"


class UpdateStoreSubscription(BaseModel):
    plan_id: int
    status: str = "active"
    current_period_end: datetime | None = None


class AdminUserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    new_password: str | None = None


class AdminStoreUsage(BaseModel):
    store_id: int
    currency: str
    total_staff: int
    total_categories: int
    total_products: int
    total_brands: int
    total_orders: int
    average_transaction: Decimal
    usage_tier: str


class AdminMetrics(BaseModel):
    total_stores: int
    total_staff: int
    total_plans: int
    total_products: int
    total_orders: int
    heavy_usage_stores: int
    light_usage_stores: int


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
