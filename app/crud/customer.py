from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    def get_by_store(self, db: Session, store_id: int) -> list[Customer]:
        return db.query(Customer).filter(Customer.store_id == store_id).all()

    def get_by_store_and_id(self, db: Session, store_id: int, customer_id: int) -> Customer | None:
        return db.query(Customer).filter(Customer.store_id == store_id, Customer.id == customer_id).first()


customer = CRUDCustomer(Customer)
