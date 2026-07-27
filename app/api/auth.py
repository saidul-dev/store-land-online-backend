from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import ProfileUpdate, ProfileUpdateResponse, RefreshRequest, UserCreate, UserRead, Token
from app.crud import user as user_crud
from app.crud.refresh_token import refresh_token as refresh_token_crud
from app.core.security import (
    verify_password,
    create_access_token,
    generate_refresh_token,
    get_current_user,
)
from app.models.user import User

router = APIRouter(tags=["auth"])


def _issue_token_pair(db: Session, user: User) -> Token:
    access_token = create_access_token(subject=user.email)
    raw_refresh_token = generate_refresh_token()
    refresh_token_crud.create(db, user_id=user.id, token=raw_refresh_token)
    return Token(access_token=access_token, refresh_token=raw_refresh_token)


@router.post("/register", response_model=UserRead, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if user_crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_crud.create_user(db, user)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, form_data.username)
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return _issue_token_pair(db, db_user)


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    db_token = refresh_token_crud.get_valid_by_token(db, payload.refresh_token)
    if db_token is None:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Rotation: the presented token is single-use — revoke it and mint a fresh pair.
    refresh_token_crud.revoke(db, db_token)
    user = db.query(User).filter(User.id == db_token.user_id).first()
    return _issue_token_pair(db, user)


@router.post("/logout", status_code=204)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    db_token = refresh_token_crud.get_valid_by_token(db, payload.refresh_token)
    if db_token is not None:
        refresh_token_crud.revoke(db, db_token)


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=ProfileUpdateResponse)
def update_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    changing_sensitive = payload.email is not None or payload.new_password is not None
    if changing_sensitive:
        if not payload.current_password or not verify_password(
            payload.current_password, current_user.hashed_password
        ):
            raise HTTPException(status_code=400, detail="Current password is incorrect")

    if payload.email is not None and payload.email != current_user.email:
        if user_crud.get_user_by_email(db, payload.email):
            raise HTTPException(status_code=400, detail="Email already registered")

    updated_user = user_crud.update_profile(
        db, current_user, name=payload.name, email=payload.email, new_password=payload.new_password
    )
    # The access token's subject is the email — reissue so an email change
    # doesn't invalidate the caller's own session mid-request.
    tokens = _issue_token_pair(db, updated_user)
    return ProfileUpdateResponse(user=updated_user, tokens=tokens)
