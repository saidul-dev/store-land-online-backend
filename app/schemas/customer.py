from datetime import datetime

from pydantic import BaseModel


class CustomerCreate(BaseModel):
    name: str
    phone: str | None = None
    email: str | None = None
    address: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None


class CustomerRead(BaseModel):
    id: int
    store_id: int
    name: str
    phone: str | None
    email: str | None
    address: str | None
    created_at: datetime

    class Config:
        from_attributes = True
