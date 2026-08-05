from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.store_membership import StoreMembership
from app.schemas.membership import MembershipCreate, MembershipRoleUpdate


class CRUDMembership(CRUDBase[StoreMembership, MembershipCreate, MembershipRoleUpdate]):
    def get_by_store(self, db: Session, store_id: int) -> list[StoreMembership]:
        return db.query(StoreMembership).filter(StoreMembership.store_id == store_id).all()

    def get_all(self, db: Session) -> list[StoreMembership]:
        return db.query(StoreMembership).order_by(StoreMembership.store_id, StoreMembership.role).all()

    def get_by_store_and_user(self, db: Session, store_id: int, user_id: int) -> StoreMembership | None:
        return (
            db.query(StoreMembership)
            .filter(StoreMembership.store_id == store_id, StoreMembership.user_id == user_id)
            .first()
        )

    def add_member(self, db: Session, *, store_id: int, user_id: int, role: str) -> StoreMembership:
        db_obj = StoreMembership(store_id=store_id, user_id=user_id, role=role)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


membership = CRUDMembership(StoreMembership)
