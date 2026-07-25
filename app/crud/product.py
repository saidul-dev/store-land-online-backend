from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def get_by_store(self, db: Session, store_id: int, *, skip: int = 0, limit: int = 100) -> list[Product]:
        return (
            db.query(Product)
            .filter(Product.store_id == store_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_store_and_id(self, db: Session, store_id: int, product_id: int) -> Product | None:
        return db.query(Product).filter(Product.store_id == store_id, Product.id == product_id).first()

    def get_by_sku(self, db: Session, store_id: int, sku: str) -> Product | None:
        return db.query(Product).filter(Product.store_id == store_id, Product.sku == sku).first()


product = CRUDProduct(Product)
