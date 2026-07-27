import re
from datetime import datetime

from pydantic import BaseModel, field_validator

RESERVED_SUBDOMAINS = {
    "www", "api", "app", "admin", "mail", "ftp", "blog", "dashboard",
    "static", "cdn", "docs", "help", "support", "status", "assets",
}


class StoreCreate(BaseModel):
    name: str
    subdomain: str

    @field_validator("subdomain")
    @classmethod
    def validate_subdomain(cls, value: str) -> str:
        value = value.strip().lower()
        if not (3 <= len(value) <= 63):
            raise ValueError("Subdomain must be between 3 and 63 characters")
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", value):
            raise ValueError(
                "Subdomain may only contain lowercase letters, digits and hyphens, "
                "and cannot start or end with a hyphen"
            )
        if value in RESERVED_SUBDOMAINS:
            raise ValueError(f"Subdomain '{value}' is reserved")
        return value


class StoreRead(BaseModel):
    id: int
    name: str
    subdomain: str
    custom_domain: str | None
    domain_verified: bool
    currency: str
    tag_line: str | None
    email: str | None
    phone_country_code: str | None
    phone_number: str | None
    country: str | None
    state: str | None
    city: str | None
    zip_code: str | None
    address: str | None
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Kept in sync by hand with CURRENCIES in the frontend's lib/format.ts.
ALLOWED_CURRENCIES = {"USD", "BDT", "EUR", "GBP", "INR"}


class StoreSettingsUpdate(BaseModel):
    name: str | None = None
    currency: str | None = None
    tag_line: str | None = None
    email: str | None = None
    phone_country_code: str | None = None
    phone_number: str | None = None
    country: str | None = None
    state: str | None = None
    city: str | None = None
    zip_code: str | None = None
    address: str | None = None

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip().upper()
        if value not in ALLOWED_CURRENCIES:
            raise ValueError(f"Currency must be one of: {', '.join(sorted(ALLOWED_CURRENCIES))}")
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Store name cannot be empty")
        return value
