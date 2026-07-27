from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    name: str | None
    email: EmailStr
    is_super_admin: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ProfileUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    current_password: str | None = None
    new_password: str | None = None


class ProfileUpdateResponse(BaseModel):
    user: UserRead
    tokens: Token
