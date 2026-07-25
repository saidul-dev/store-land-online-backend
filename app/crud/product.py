from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.schemas.product import ProductCreate, ProductUpdate, ProductVariantCreate, ProductVariantUpdate


class DuplicateSKUError(Exception):
    def __init__(self, sku: str) -> None:
        self.sku = sku


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def get_by_store(
        self,
        db: Session,
        store_id: int,
        *,
        category_id: int | None = None,
        brand_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Product]:
        query = db.query(Product).filter(Product.store_id == store_id)
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)
        if brand_id is not None:
            query = query.filter(Product.brand_id == brand_id)
        return query.offset(skip).limit(limit).all()

    def count_by_store(
        self,
        db: Session,
        store_id: int,
        *,
        category_id: int | None = None,
        brand_id: int | None = None,
    ) -> int:
        query = db.query(Product).filter(Product.store_id == store_id)
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)
        if brand_id is not None:
            query = query.filter(Product.brand_id == brand_id)
        return query.count()

    def get_by_store_and_id(self, db: Session, store_id: int, product_id: int) -> Product | None:
        return db.query(Product).filter(Product.store_id == store_id, Product.id == product_id).first()

    def _check_sku_available(self, db: Session, store_id: int, sku: str, seen: set[str]) -> None:
        if sku in seen:
            raise DuplicateSKUError(sku)
        seen.add(sku)
        if db.query(ProductVariant).filter(ProductVariant.store_id == store_id, ProductVariant.sku == sku).first():
            raise DuplicateSKUError(sku)

    def create_with_variants(self, db: Session, *, store_id: int, payload: ProductCreate) -> Product:
        seen_skus: set[str] = set()
        for variant_in in payload.variants:
            self._check_sku_available(db, store_id, variant_in.sku, seen_skus)

        product = Product(
            store_id=store_id,
            category_id=payload.category_id,
            brand_id=payload.brand_id,
            name=payload.name,
            description=payload.description,
        )
        for variant_in in payload.variants:
            product.variants.append(
                ProductVariant(
                    store_id=store_id,
                    sku=variant_in.sku,
                    price=variant_in.price,
                    stock_quantity=variant_in.stock_quantity,
                    attributes=variant_in.attributes,
                )
            )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def add_variant(self, db: Session, *, store_id: int, product: Product, variant_in: ProductVariantCreate) -> ProductVariant:
        self._check_sku_available(db, store_id, variant_in.sku, set())
        db_variant = ProductVariant(
            store_id=store_id,
            product_id=product.id,
            sku=variant_in.sku,
            price=variant_in.price,
            stock_quantity=variant_in.stock_quantity,
            attributes=variant_in.attributes,
        )
        db.add(db_variant)
        db.commit()
        db.refresh(db_variant)
        return db_variant

    def get_variant(self, db: Session, store_id: int, product_id: int, variant_id: int) -> ProductVariant | None:
        return (
            db.query(ProductVariant)
            .filter(
                ProductVariant.store_id == store_id,
                ProductVariant.product_id == product_id,
                ProductVariant.id == variant_id,
            )
            .first()
        )


product = CRUDProduct(Product)
# Update/remove reuse CRUDBase directly — only creation needs the custom SKU/nesting logic above.
variant = CRUDBase[ProductVariant, ProductVariantCreate, ProductVariantUpdate](ProductVariant)
