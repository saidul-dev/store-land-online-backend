from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql import false as sa_false

from app.db.base import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    subdomain = Column(String(63), unique=True, index=True, nullable=False)
    custom_domain = Column(String(255), unique=True, index=True, nullable=True)
    domain_verified = Column(Boolean, nullable=False, default=False, server_default=sa_false())
    currency = Column(String(3), nullable=False, default="USD", server_default="USD")
    tag_line = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone_country_code = Column(String(5), nullable=True)
    phone_number = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User")
