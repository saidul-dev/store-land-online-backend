from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.db.base import Base


class SiteContent(Base):
    __tablename__ = "site_content"

    id = Column(Integer, primary_key=True, index=True)
    hero_badge = Column(String(255), nullable=True)
    hero_heading = Column(String(500), nullable=False, default="Launch your online store in minutes.")
    hero_subheading = Column(
        Text,
        nullable=False,
        default=(
            "AutoCommerce gives you a storefront, a catalog, a team, and the analytics to run "
            "them — all from one dashboard. No code required to get started."
        ),
    )
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
