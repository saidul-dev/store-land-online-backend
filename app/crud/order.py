from decimal import Decimal

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderItemCreate, OrderStatusUpdate


class ProductNotFoundError(Exception):
    def __init__(self, product_id: int) -> None:
        self.product_id = product_id


class InsufficientStockError(Exception):
    def __init__(self, product_name: str, available: int) -> None:
        self.product_name = product_name
        self.available = available


class CRUDOrder(CRUDBase[Order, OrderItemCreate, OrderStatusUpdate]):
    def get_by_store(self, db: Session, store_id: int, *, skip: int = 0, limit: int = 100) -> list[Order]:
        return (
            db.query(Order)
            .filter(Order.store_id == store_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

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
            db_product = (
                db.query(Product)
                .filter(
                    Product.store_id == store_id,
                    Product.id == item_in.product_id,
                    Product.is_active.is_(True),
                )
                .first()
            )
            if db_product is None:
                raise ProductNotFoundError(item_in.product_id)
            if db_product.stock_quantity < item_in.quantity:
                raise InsufficientStockError(db_product.name, db_product.stock_quantity)

            db_product.stock_quantity -= item_in.quantity
            unit_price = db_product.price
            total += unit_price * item_in.quantity
            order_items.append(
                OrderItem(product_id=db_product.id, quantity=item_in.quantity, unit_price=unit_price)
            )

        order = Order(store_id=store_id, customer_id=customer_id, total_amount=total, items=order_items)
        db.add(order)
        db.commit()
        db.refresh(order)
        return order


order = CRUDOrder(Order)
