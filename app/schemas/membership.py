from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from app.core.permissions import ASSIGNABLE_ROLES


def _validate_role(value: str) -> str:
    value = value.strip().lower()
    if value not in ASSIGNABLE_ROLES:
        raise ValueError(f"Role must be one of {sorted(ASSIGNABLE_ROLES)}")
    return value


class MembershipCreate(BaseModel):
    email: EmailStr
    role: str
    # When the email isn't already registered, providing these creates the
    # account inline instead of 404ing. Ignored if the user already exists.
    name: str | None = None
    password: str | None = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        return _validate_role(value)


class MembershipRoleUpdate(BaseModel):
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        return _validate_role(value)


class MembershipRead(BaseModel):
    id: int
    store_id: int
    user_id: int
    user_email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
