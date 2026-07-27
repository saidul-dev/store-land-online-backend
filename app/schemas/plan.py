from decimal import Decimal

from pydantic import BaseModel


class PlanRead(BaseModel):
    id: int
    name: str
    slug: str
    price: Decimal
    billing_cycle: str
    max_products: int | None
    max_staff: int | None
    custom_domain_allowed: bool
    is_active: bool

    class Config:
        from_attributes = True
