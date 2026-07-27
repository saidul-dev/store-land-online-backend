from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.plan import Plan


class CRUDPlan(CRUDBase[Plan, Plan, Plan]):
    def get_by_slug(self, db: Session, slug: str) -> Plan | None:
        return db.query(Plan).filter(Plan.slug == slug).first()

    def get_active(self, db: Session) -> list[Plan]:
        return db.query(Plan).filter(Plan.is_active.is_(True)).all()


plan = CRUDPlan(Plan)
