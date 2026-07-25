from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.brand import Brand
from app.schemas.brand import BrandCreate, BrandUpdate


class CRUDBrand(CRUDBase[Brand, BrandCreate, BrandUpdate]):
    def get_by_store(self, db: Session, store_id: int) -> list[Brand]:
        return db.query(Brand).filter(Brand.store_id == store_id).all()

    def get_by_store_and_id(self, db: Session, store_id: int, brand_id: int) -> Brand | None:
        return db.query(Brand).filter(Brand.store_id == store_id, Brand.id == brand_id).first()

    def get_by_slug(self, db: Session, store_id: int, slug: str) -> Brand | None:
        return db.query(Brand).filter(Brand.store_id == store_id, Brand.slug == slug).first()


brand = CRUDBrand(Brand)
