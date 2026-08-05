from sqlalchemy import Boolean, Column, Integer, String, DateTime, func
from sqlalchemy.sql import false as sa_false

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_super_admin = Column(Boolean, nullable=False, default=False, server_default=sa_false())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
