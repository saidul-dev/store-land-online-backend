from sqlalchemy.orm import Session

from app.models.post import Post
from app.schemas.post import PostCreate


def create_post(db: Session, post: PostCreate, author_id: int) -> Post:
    db_post = Post(title=post.title, content=post.content, author_id=author_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_post(db: Session, post_id: int) -> Post | None:
    return db.query(Post).filter(Post.id == post_id).first()


def get_posts(db: Session, skip: int = 0, limit: int = 100) -> list[Post]:
    return db.query(Post).offset(skip).limit(limit).all()


def update_post(db: Session, db_post: Post, post: PostCreate) -> Post:
    db_post.title = post.title
    db_post.content = post.content
    db.commit()
    db.refresh(db_post)
    return db_post


def delete_post(db: Session, db_post: Post) -> None:
    db.delete(db_post)
    db.commit()
