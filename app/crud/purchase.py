from decimal import Decimal

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.product_variant import ProductVariant
from app.models.purchase import Purchase, PurchaseItem
from app.schemas.purchase import PurchaseCreate, PurchaseStatusUpdate


class VariantNotFoundError(Exception):
    def __init__(self, variant_id: int) -> None:
        self.variant_id = variant_id


class InvalidPurchaseStatusError(Exception):
    def __init__(self, current_status: str) -> None:
        self.current_status = current_status


class CRUDPurchase(CRUDBase[Purchase, PurchaseCreate, PurchaseStatusUpdate]):
    def get_by_store(self, db: Session, store_id: int, *, skip: int = 0, limit: int = 100) -> list[Purchase]:
        return (
            db.query(Purchase)
            .filter(Purchase.store_id == store_id)
            .order_by(Purchase.created_at.desc(), Purchase.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_store(self, db: Session, store_id: int) -> int:
        return db.query(Purchase).filter(Purchase.store_id == store_id).count()

    def get_by_store_and_id(self, db: Session, store_id: int, purchase_id: int) -> Purchase | None:
        return db.query(Purchase).filter(Purchase.store_id == store_id, Purchase.id == purchase_id).first()

    def create_with_items(
        self,
        db: Session,
        *,
        store_id: int,
        created_by_id: int,
        payload: PurchaseCreate,
    ) -> Purchase:
        items: list[PurchaseItem] = []
        total = Decimal("0")
        for item_in in payload.items:
            db_variant = (
                db.query(ProductVariant)
                .filter(ProductVariant.store_id == store_id, ProductVariant.id == item_in.variant_id)
                .first()
            )
            if db_variant is None:
                raise VariantNotFoundError(item_in.variant_id)
            total += item_in.unit_cost * item_in.quantity
            items.append(
                PurchaseItem(variant_id=item_in.variant_id, quantity=item_in.quantity, unit_cost=item_in.unit_cost)
            )

        purchase = Purchase(
            store_id=store_id,
            supplier_id=payload.supplier_id,
            created_by_id=created_by_id,
            notes=payload.notes,
            total_cost=total,
            items=items,
        )
        db.add(purchase)
        db.commit()
        db.refresh(purchase)
        return purchase

    def receive(self, db: Session, purchase: Purchase) -> Purchase:
        if purchase.status != "pending":
            raise InvalidPurchaseStatusError(purchase.status)
        for item in purchase.items:
            item.variant.stock_quantity += item.quantity
        purchase.status = "received"
        db.commit()
        db.refresh(purchase)
        return purchase

    def cancel(self, db: Session, purchase: Purchase) -> Purchase:
        if purchase.status != "pending":
            raise InvalidPurchaseStatusError(purchase.status)
        purchase.status = "cancelled"
        db.commit()
        db.refresh(purchase)
        return purchase


purchase = CRUDPurchase(Purchase)
