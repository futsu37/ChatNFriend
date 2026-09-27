import uuid
from collections.abc import Sequence

from sqlmodel import Session, col, select

from backend.models import Post, User
from backend.schemas.post import PostCreate, PostUpdate, PostUpdateMe


def get_posts(session: Session, limit: int, offset: int) -> tuple[Sequence[Post],int]:
    posts_statement = select(Post).order_by(col(Post.created_at).desc()).offset(offset).limit(limit)
    posts_db = session.exec(posts_statement).all()
    count = posts_db.__len__()
    return posts_db, count

def get_user_posts(session: Session, user_id: uuid.UUID, limit: int, offset: int) -> tuple[Sequence[Post],int]:
    posts_statement = select(Post).where(Post.owner_id == user_id).order_by(col(Post.created_at).desc()).offset(offset).limit(limit)
    posts_db = session.exec(posts_statement).all()
    count = posts_db.__len__()
    return posts_db, count

def create_post(session: Session, user: User, post_in: PostCreate) -> Post:
    post = Post.model_validate(post_in, update={"owner_id": user.id})
    session.add(post)
    session.commit()
    session.refresh(post)
    return post

def update_post(session: Session, post: Post, update_in: PostUpdate | PostUpdateMe) -> Post:
    update_data = update_in.model_dump(exclude_unset=True)
    post.sqlmodel_update(update_data)
    session.add(post)
    session.commit()
    session.refresh(post)
    return post

def delete_post(session: Session, post: Post):
    session.delete(post)
    session.commit()
    return "Post was successfully deleted"