from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ProductVariantCreate(BaseModel):
    sku: str
    price: Decimal = Field(gt=0)
    stock_quantity: int = Field(default=0, ge=0)
    attributes: dict[str, str] = Field(default_factory=dict)


class ProductVariantUpdate(BaseModel):
    price: Decimal | None = Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)
    attributes: dict[str, str] | None = None
    is_active: bool | None = None


class ProductVariantRead(BaseModel):
    id: int
    product_id: int
    sku: str
    price: Decimal
    stock_quantity: int
    attributes: dict[str, str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductImageRead(BaseModel):
    id: int
    product_id: int
    file_path: str
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    category_id: int | None = None
    brand_id: int | None = None
    variants: list[ProductVariantCreate] = Field(min_length=1)


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    brand_id: int | None = None
    is_active: bool | None = None


class ProductRead(BaseModel):
    id: int
    store_id: int
    category_id: int | None
    brand_id: int | None
    name: str
    description: str | None
    is_active: bool
    variants: list[ProductVariantRead]
    images: list[ProductImageRead]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
