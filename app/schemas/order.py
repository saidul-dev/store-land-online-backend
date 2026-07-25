from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.core.order_status import ORDER_STATUSES


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItemRead(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal

    class Config:
        from_attributes = True


class OrderRead(BaseModel):
    id: int
    store_id: int
    customer_id: int
    status: str
    total_amount: Decimal
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
