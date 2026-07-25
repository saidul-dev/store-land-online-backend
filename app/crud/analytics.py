from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.security import utcnow
from app.models.order import Order
from app.models.product import Product


def _naive(dt: datetime) -> datetime:
    # Order.created_at is tz-aware on Postgres but SQLite (tests) hands back naive
    # datetimes — normalize both to naive-UTC before comparing, same reasoning as
    # app.core.security.utcnow.
    return dt.replace(tzinfo=None) if dt.tzinfo else dt


def get_summary(db: Session, store_id: int, *, days: int = 30) -> dict:
    cutoff = utcnow() - timedelta(days=days)

    orders = db.query(Order).filter(Order.store_id == store_id).all()
    windowed = [o for o in orders if _naive(o.created_at) >= cutoff]
    non_cancelled = [o for o in windowed if o.status != "cancelled"]

    total_revenue = sum((o.total_amount for o in non_cancelled), Decimal("0"))
    average_order_value = (total_revenue / len(non_cancelled)) if non_cancelled else Decimal("0")

    total_products = (
        db.query(Product).filter(Product.store_id == store_id, Product.is_active.is_(True)).count()
    )

    daily_totals: dict = defaultdict(lambda: {"orders": 0, "revenue": Decimal("0")})
    for o in windowed:
        day = _naive(o.created_at).date()
        daily_totals[day]["orders"] += 1
        if o.status != "cancelled":
            daily_totals[day]["revenue"] += o.total_amount
    daily = [
        {"date": day, "orders": v["orders"], "revenue": v["revenue"]}
        for day, v in sorted(daily_totals.items())
    ]

    return {
        "total_revenue": total_revenue,
        "total_orders": len(windowed),
        "average_order_value": average_order_value,
        "total_products": total_products,
        "total_customers": len({o.customer_id for o in windowed}),
        "pending_orders": sum(1 for o in windowed if o.status == "pending"),
        "processing_orders": sum(1 for o in windowed if o.status == "processing"),
        "cancelled_orders": sum(1 for o in windowed if o.status == "cancelled"),
        "daily": daily,
    }
