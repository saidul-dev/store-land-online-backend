from sqlalchemy import Column, DateTime, Integer, String, func

from app.db.base import Base


class SiteFeature(Base):
    __tablename__ = "site_features"

    id = Column(Integer, primary_key=True, index=True)
    icon = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
