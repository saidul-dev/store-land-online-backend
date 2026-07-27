from sqlalchemy.orm import Session

from app.models.plan import Plan

# Mirrors the data inserted by the add_plans_and_subscriptions migration —
# that migration seeds the real database directly (via raw SQL, decoupled from
# the ORM model), while this seeds the ephemeral per-test sqlite database used
# by tests/conftest.py. Keep the two in sync by hand.
DEFAULT_PLANS = [
    {
        "name": "Free", "slug": "free", "price": 0, "billing_cycle": "trial",
        "max_products": 20, "max_staff": 3, "custom_domain_allowed": False,
    },
    {
        "name": "Basic", "slug": "basic", "price": 999, "billing_cycle": "monthly",
        "max_products": 200, "max_staff": 5, "custom_domain_allowed": True,
    },
    {
        "name": "Pro", "slug": "pro", "price": 2499, "billing_cycle": "monthly",
        "max_products": None, "max_staff": None, "custom_domain_allowed": True,
    },
]


def seed_default_plans(db: Session) -> None:
    for data in DEFAULT_PLANS:
        if db.query(Plan).filter(Plan.slug == data["slug"]).first() is None:
            db.add(Plan(**data))
    db.commit()
