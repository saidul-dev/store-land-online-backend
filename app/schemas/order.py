from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.core.order_status import ORDER_STATUSES
from app.core.payment_method import PAYMENT_METHODS


class OrderItemCreate(BaseModel):
    variant_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(min_length=1)
    payment_method: str = "cod"
    contact_name: str
    contact_email: str
    contact_phone: str
    shipping_address: str
    shipping_city: str
    shipping_postal_code: str | None = None

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in PAYMENT_METHODS:
            raise ValueError(f"Payment method must be one of {sorted(PAYMENT_METHODS)}")
        return value


class OrderItemRead(BaseModel):
    id: int
    variant_id: int
    quantity: int
    unit_price: Decimal

    class Config:
        from_attributes = True


class OrderRead(BaseModel):
    id: int
    store_id: int
    customer_id: int | None
    status: str
    total_amount: Decimal
    payment_method: str
    contact_name: str
    contact_email: str
    contact_phone: str
    shipping_address: str
    shipping_city: str
    shipping_postal_code: str | None
    items: list[OrderItemRead]
    created_at: datetime

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in ORDER_STATUSES:
            raise ValueError(f"Status must be one of {sorted(ORDER_STATUSES)}")
        return value
