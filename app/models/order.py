from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    # Nullable — guest checkout has no user account, only the contact_* fields below.
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # Optional link to a store-managed Customer record (separate from the User
    # account above) — set for manually-created sales, null for normal checkout.
    customer_ref_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    status = Column(String(20), nullable=False, default="pending", server_default="pending")
    # "online" = storefront checkout, "manual" = staff-created sale (POST /orders/manual).
    channel = Column(String(10), nullable=False, default="online", server_default="online")
    total_amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(20), nullable=False, default="cod", server_default="cod")
    contact_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(30), nullable=False)
    shipping_address = Column(Text, nullable=False)
    shipping_city = Column(String(100), nullable=False)
    shipping_postal_code = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    store = relationship("Store")
    customer = relationship("User")
    customer_ref = relationship("Customer")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    variant = relationship("ProductVariant")
