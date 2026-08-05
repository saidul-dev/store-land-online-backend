from decimal import Decimal

from pydantic import BaseModel


class PlanCreate(BaseModel):
    name: str
    slug: str
    price: Decimal = Decimal("0")
    billing_cycle: str = "monthly"
    max_products: int | None = None
    max_staff: int | None = None
    custom_domain_allowed: bool = False
    is_active: bool = True


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
