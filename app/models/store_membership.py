from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class StoreMembership(Base):
    __tablename__ = "store_memberships"
    __table_args__ = (UniqueConstraint("store_id", "user_id", name="uq_store_membership_store_user"),)

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(30), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    store = relationship("Store")
    user = relationship("User")

    @property
    def user_email(self) -> str:
        return self.user.email
