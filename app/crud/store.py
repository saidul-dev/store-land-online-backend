from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.store import Store
from app.schemas.store import StoreCreate, StoreSettingsUpdate


class CRUDStore(CRUDBase[Store, StoreCreate, StoreSettingsUpdate]):
    def get_by_subdomain(self, db: Session, subdomain: str) -> Store | None:
        return db.query(Store).filter(Store.subdomain == subdomain.lower()).first()

    def get_by_custom_domain(self, db: Session, domain: str) -> Store | None:
        return (
            db.query(Store)
            .filter(Store.custom_domain == domain.lower(), Store.domain_verified.is_(True))
            .first()
        )

    def get_by_owner(self, db: Session, owner_id: int) -> list[Store]:
        return db.query(Store).filter(Store.owner_id == owner_id).all()


store = CRUDStore(Store)
