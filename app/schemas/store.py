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
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
