from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.subscription import Subscription


class CRUDSubscription(CRUDBase[Subscription, Subscription, Subscription]):
    def get_by_store(self, db: Session, store_id: int) -> Subscription | None:
        return db.query(Subscription).filter(Subscription.store_id == store_id).first()


subscription = CRUDSubscription(Subscription)
