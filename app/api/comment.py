from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.comment import CommentCreate, CommentRead
from app.crud import comment as comment_crud, post as post_crud
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])


@router.post("/", response_model=CommentRead, status_code=201)
def create_comment(
    post_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_post = post_crud.get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return comment_crud.create_comment(db, comment, post_id=post_id, author_id=current_user.id)


@router.get("/", response_model=list[CommentRead])
def list_comments(post_id: int, db: Session = Depends(get_db)):
    return comment_crud.get_comments_for_post(db, post_id)
