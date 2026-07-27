from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, func
from sqlalchemy.sql import true as sa_true

from app.db.base import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, index=True, nullable=False)
    price = Column(Numeric(10, 2), nullable=False, default=0)
    billing_cycle = Column(String(20), nullable=False, default="monthly")
    # null = unlimited
    max_products = Column(Integer, nullable=True)
    max_staff = Column(Integer, nullable=True)
    custom_domain_allowed = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default=sa_true())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
