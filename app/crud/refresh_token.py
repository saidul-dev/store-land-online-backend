from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_refresh_token, utcnow
from app.models.refresh_token import RefreshToken


class CRUDRefreshToken:
    def create(self, db: Session, *, user_id: int, token: str) -> RefreshToken:
        db_obj = RefreshToken(
            user_id=user_id,
            token_hash=hash_refresh_token(token),
            expires_at=utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_valid_by_token(self, db: Session, token: str) -> RefreshToken | None:
        db_obj = (
            db.query(RefreshToken)
            .filter(
                RefreshToken.token_hash == hash_refresh_token(token),
                RefreshToken.revoked_at.is_(None),
            )
            .first()
        )
        if db_obj is None or db_obj.expires_at < utcnow():
            return None
        return db_obj

    def revoke(self, db: Session, db_obj: RefreshToken) -> None:
        db_obj.revoked_at = utcnow()
        db.commit()

    def revoke_all_for_user(self, db: Session, user_id: int) -> None:
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None)
        ).update({"revoked_at": utcnow()})
        db.commit()


refresh_token = CRUDRefreshToken()
