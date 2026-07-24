from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.post import PostCreate, PostRead
from app.crud import post as post_crud
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostRead, status_code=201)
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return post_crud.create_post(db, post, author_id=current_user.id)


@router.get("/", response_model=list[PostRead])
def list_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return post_crud.get_posts(db, skip=skip, limit=limit)


@router.get("/{post_id}", response_model=PostRead)
def read_post(post_id: int, db: Session = Depends(get_db)):
    db_post = post_crud.get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post


@router.put("/{post_id}", response_model=PostRead)
def update_post(
    post_id: int,
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_post = post_crud.get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your post")
    return post_crud.update_post(db, db_post, post)


@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_post = post_crud.get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your post")
    post_crud.delete_post(db, db_post)
