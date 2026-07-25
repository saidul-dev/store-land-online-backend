import re
from datetime import datetime

from pydantic import BaseModel, field_validator

SLUG_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")


def _validate_slug(value: str) -> str:
    value = value.strip().lower()
    if not SLUG_RE.fullmatch(value):
        raise ValueError("Slug may only contain lowercase letters, digits and hyphens")
    return value


class CategoryCreate(BaseModel):
    name: str
    slug: str
    parent_id: int | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        return _validate_slug(value)


class CategoryUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    parent_id: int | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str | None) -> str | None:
        return _validate_slug(value) if value is not None else value


class CategoryRead(BaseModel):
    id: int
    store_id: int
    parent_id: int | None
    name: str
    slug: str
    created_at: datetime

    class Config:
        from_attributes = True
