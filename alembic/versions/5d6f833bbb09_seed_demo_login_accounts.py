"""seed demo login accounts

Revision ID: 5d6f833bbb09
Revises: 219f74759916
Create Date: 2026-08-05 00:00:00.000000

Seeds the two accounts advertised on the frontend login page's "Demo
credentials" panel (src/components/demo-credentials.tsx), so a fresh
migrate always leaves them in place: a platform super admin and a
store owner who owns "Demo Store". Mirrors the normal store-registration
flow (owner_id + "owner" membership + trialing free-plan subscription)
so the owner account behaves like any real store owner.
"""
from datetime import datetime, timedelta, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.core.security import hash_password

# revision identifiers, used by Alembic.
revision: str = '5d6f833bbb09'
down_revision: Union[str, Sequence[str], None] = '219f74759916'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SUPERADMIN_EMAIL = "admin@autocommerce.com"
SUPERADMIN_PASSWORD = "12345678"

OWNER_EMAIL = "owner@autocommerce.com"
OWNER_PASSWORD = "12345678"
STORE_NAME = "Demo Store"
STORE_SUBDOMAIN = "demo"

TRIAL_DAYS = 7


def upgrade() -> None:
    conn = op.get_bind()

    conn.execute(
        sa.text(
            """
            INSERT INTO users (email, hashed_password, is_super_admin)
            VALUES (:email, :hashed_password, true)
            ON CONFLICT (email) DO NOTHING
            """
        ),
        {"email": SUPERADMIN_EMAIL, "hashed_password": hash_password(SUPERADMIN_PASSWORD)},
    )

    conn.execute(
        sa.text(
            """
            INSERT INTO users (email, hashed_password, is_super_admin)
            VALUES (:email, :hashed_password, false)
            ON CONFLICT (email) DO NOTHING
            """
        ),
        {"email": OWNER_EMAIL, "hashed_password": hash_password(OWNER_PASSWORD)},
    )

    owner_id = conn.execute(
        sa.text("SELECT id FROM users WHERE email = :email"),
        {"email": OWNER_EMAIL},
    ).scalar_one()

    conn.execute(
        sa.text(
            """
            INSERT INTO stores (name, subdomain, owner_id)
            VALUES (:name, :subdomain, :owner_id)
            ON CONFLICT (subdomain) DO NOTHING
            """
        ),
        {"name": STORE_NAME, "subdomain": STORE_SUBDOMAIN, "owner_id": owner_id},
    )

    store_id = conn.execute(
        sa.text("SELECT id FROM stores WHERE subdomain = :subdomain"),
        {"subdomain": STORE_SUBDOMAIN},
    ).scalar_one()

    conn.execute(
        sa.text(
            """
            INSERT INTO store_memberships (store_id, user_id, role)
            VALUES (:store_id, :owner_id, 'owner')
            ON CONFLICT (store_id, user_id) DO NOTHING
            """
        ),
        {"store_id": store_id, "owner_id": owner_id},
    )

    free_plan_id = conn.execute(
        sa.text("SELECT id FROM plans WHERE slug = 'free'"),
    ).scalar_one_or_none()

    if free_plan_id is not None:
        conn.execute(
            sa.text(
                """
                INSERT INTO subscriptions (store_id, plan_id, status, current_period_end)
                VALUES (:store_id, :plan_id, 'trialing', :period_end)
                ON CONFLICT (store_id) DO NOTHING
                """
            ),
            {
                "store_id": store_id,
                "plan_id": free_plan_id,
                "period_end": datetime.now(timezone.utc) + timedelta(days=TRIAL_DAYS),
            },
        )


def downgrade() -> None:
    conn = op.get_bind()

    store_id = conn.execute(
        sa.text("SELECT id FROM stores WHERE subdomain = :subdomain"),
        {"subdomain": STORE_SUBDOMAIN},
    ).scalar_one_or_none()

    if store_id is not None:
        conn.execute(sa.text("DELETE FROM subscriptions WHERE store_id = :store_id"), {"store_id": store_id})
        conn.execute(sa.text("DELETE FROM store_memberships WHERE store_id = :store_id"), {"store_id": store_id})
        conn.execute(sa.text("DELETE FROM stores WHERE id = :store_id"), {"store_id": store_id})

    conn.execute(
        sa.text(
            """
            DELETE FROM refresh_tokens
            WHERE user_id IN (SELECT id FROM users WHERE email IN (:owner, :admin))
            """
        ),
        {"owner": OWNER_EMAIL, "admin": SUPERADMIN_EMAIL},
    )
    conn.execute(sa.text("DELETE FROM users WHERE email IN (:owner, :admin)"), {
        "owner": OWNER_EMAIL,
        "admin": SUPERADMIN_EMAIL,
    })
