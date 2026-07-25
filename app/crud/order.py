from decimal import Decimal

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.schemas.order import OrderItemCreate, OrderStatusUpdate


class VariantNotFoundError(Exception):
    def __init__(self, variant_id: int) -> None:
        self.variant_id = variant_id


class InsufficientStockError(Exception):
    def __init__(self, sku: str, available: int) -> None:
        self.sku = sku
        self.available = available


class CRUDOrder(CRUDBase[Order, OrderItemCreate, OrderStatusUpdate]):
    def get_by_store(self, db: Session, store_id: int, *, skip: int = 0, limit: int = 100) -> list[Order]:
        return (
            db.query(Order)
            .filter(Order.store_id == store_id)
            # id as a tiebreaker: created_at alone isn't unique enough — orders
            # placed in quick succession (e.g. in tests) can share a timestamp.
            .order_by(Order.created_at.desc(), Order.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_store(self, db: Session, store_id: int) -> int:
        return db.query(Order).filter(Order.store_id == store_id).count()

    def get_by_store_and_id(self, db: Session, store_id: int, order_id: int) -> Order | None:
        return db.query(Order).filter(Order.store_id == store_id, Order.id == order_id).first()

    def get_by_customer(self, db: Session, store_id: int, customer_id: int) -> list[Order]:
        return (
            db.query(Order)
            .filter(Order.store_id == store_id, Order.customer_id == customer_id)
            .all()
        )

    def create_with_items(
        self,
        db: Session,
        *,
        store_id: int,
        customer_id: int,
        items_in: list[OrderItemCreate],
    ) -> Order:
        order_items = []
        total = Decimal("0")

        # No row locking here (SQLite test backend doesn't support SELECT FOR UPDATE) —
        # fine for a single-process demo, but concurrent checkouts on Postgres could
        # oversell stock; add a locking read before this goes to production.
        for item_in in items_in:
            db_variant = (
                db.query(ProductVariant)
                .join(Product, Product.id == ProductVariant.product_id)
                .filter(
                    ProductVariant.store_id == store_id,
                    ProductVariant.id == item_in.variant_id,
                    ProductVariant.is_active.is_(True),
                    Product.is_active.is_(True),
                )
                .first()
            )
            if db_variant is None:
                raise VariantNotFoundError(item_in.variant_id)
            if db_variant.stock_quantity < item_in.quantity:
                raise InsufficientStockError(db_variant.sku, db_variant.stock_quantity)

            db_variant.stock_quantity -= item_in.quantity
            unit_price = db_variant.price
            total += unit_price * item_in.quantity
            order_items.append(
                OrderItem(variant_id=db_variant.id, quantity=item_in.quantity, unit_price=unit_price)
            )

        order = Order(store_id=store_id, customer_id=customer_id, total_amount=total, items=order_items)
        db.add(order)
        db.commit()
        db.refresh(order)
        return order


order = CRUDOrder(Order)
