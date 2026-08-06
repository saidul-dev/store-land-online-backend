from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.core.purchase_status import PURCHASE_STATUSES


class PurchaseItemCreate(BaseModel):
    variant_id: int
    quantity: int = Field(gt=0)
    unit_cost: Decimal = Field(ge=0)


class PurchaseCreate(BaseModel):
    supplier_id: int
    notes: str | None = None
    items: list[PurchaseItemCreate] = Field(min_length=1)


class PurchaseItemRead(BaseModel):
    id: int
    variant_id: int
    quantity: int
    unit_cost: Decimal

    class Config:
        from_attributes = True


class PurchaseRead(BaseModel):
    id: int
    store_id: int
    supplier_id: int
    status: str
    notes: str | None
    total_cost: Decimal
    items: list[PurchaseItemRead]
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in PURCHASE_STATUSES:
            raise ValueError(f"Status must be one of {sorted(PURCHASE_STATUSES)}")
        return value
