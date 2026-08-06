from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate


class CRUDSupplier(CRUDBase[Supplier, SupplierCreate, SupplierUpdate]):
    def get_by_store(self, db: Session, store_id: int) -> list[Supplier]:
        return db.query(Supplier).filter(Supplier.store_id == store_id).all()

    def get_by_store_and_id(self, db: Session, store_id: int, supplier_id: int) -> Supplier | None:
        return db.query(Supplier).filter(Supplier.store_id == store_id, Supplier.id == supplier_id).first()


supplier = CRUDSupplier(Supplier)
