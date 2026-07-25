from datetime import datetime

from pydantic import BaseModel, field_validator

from app.schemas.category import _validate_slug


class BrandCreate(BaseModel):
    name: str
    slug: str

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        return _validate_slug(value)


class BrandUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str | None) -> str | None:
        return _validate_slug(value) if value is not None else value


class BrandRead(BaseModel):
    id: int
    store_id: int
    name: str
    slug: str
    created_at: datetime

    class Config:
        from_attributes = True
