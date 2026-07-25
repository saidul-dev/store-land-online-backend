from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def get_by_store(self, db: Session, store_id: int) -> list[Category]:
        return db.query(Category).filter(Category.store_id == store_id).all()

    def get_by_store_and_id(self, db: Session, store_id: int, category_id: int) -> Category | None:
        return db.query(Category).filter(Category.store_id == store_id, Category.id == category_id).first()

    def get_by_slug(self, db: Session, store_id: int, slug: str) -> Category | None:
        return db.query(Category).filter(Category.store_id == store_id, Category.slug == slug).first()


category = CRUDCategory(Category)
