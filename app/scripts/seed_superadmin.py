"""Create (or promote) the platform super-admin from SUPERADMIN_EMAIL / SUPERADMIN_PASSWORD.

Run once per environment: `python -m app.scripts.seed_superadmin`
Idempotent — safe to re-run; it only sets the password on first creation.
"""

from app.core.config import settings
from app.core.security import hash_password
from app.crud.user import get_user_by_email
from app.db.session import SessionLocal
from app.models.user import User


def run() -> None:
    if not settings.SUPERADMIN_EMAIL or not settings.SUPERADMIN_PASSWORD:
        raise SystemExit("Set SUPERADMIN_EMAIL and SUPERADMIN_PASSWORD in .env before running this.")

    db = SessionLocal()
    try:
        user = get_user_by_email(db, settings.SUPERADMIN_EMAIL)
        if user is None:
            user = User(
                email=settings.SUPERADMIN_EMAIL,
                hashed_password=hash_password(settings.SUPERADMIN_PASSWORD),
                is_super_admin=True,
            )
            db.add(user)
            db.commit()
            print(f"Created super-admin: {settings.SUPERADMIN_EMAIL}")
        elif not user.is_super_admin:
            user.is_super_admin = True
            db.commit()
            print(f"Promoted existing user to super-admin: {settings.SUPERADMIN_EMAIL}")
        else:
            print(f"{settings.SUPERADMIN_EMAIL} is already a super-admin — nothing to do.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
