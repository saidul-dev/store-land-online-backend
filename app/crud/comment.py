from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.schemas.comment import CommentCreate


def create_comment(db: Session, comment: CommentCreate, post_id: int, author_id: int) -> Comment:
    db_comment = Comment(content=comment.content, post_id=post_id, author_id=author_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comments_for_post(db: Session, post_id: int) -> list[Comment]:
    return db.query(Comment).filter(Comment.post_id == post_id).all()
