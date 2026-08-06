from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate, *, name: str | None = None) -> User:
    db_user = User(email=user.email, hashed_password=hash_password(user.password), name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_profile(
    db: Session,
    user: User,
    *,
    name: str | None,
    phone: str | None,
    email: str | None,
    new_password: str | None,
) -> User:
    if name is not None:
        user.name = name
    if phone is not None:
        user.phone = phone
    if email is not None:
        user.email = email
    if new_password is not None:
        user.hashed_password = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user
