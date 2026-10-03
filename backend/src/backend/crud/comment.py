import uuid
from collections.abc import Sequence

from sqlmodel import Session, col, select

from backend.models import Comment
from backend.schemas.comment import CommentCreate, CommentUpdate


def get_comments(session: Session, limit: int, offset: int) -> tuple[Sequence[Comment],int]:
    comments_statement = select(Comment).order_by(col(Comment.created_at).desc()).offset(offset).limit(limit)
    comments_db = session.exec(comments_statement).all()
    count = comments_db.__len__()
    return comments_db, count

def get_user_comments(session: Session, user_id: uuid.UUID, limit: int, offset: int) -> tuple[Sequence[Comment],int]:
    comments_statement = select(Comment).where(Comment.owner_id == user_id).order_by(col(Comment.created_at).desc()).offset(offset).limit(limit)
    comments_db = session.exec(comments_statement).all()
    count = comments_db.__len__()
    return comments_db, count

def create_comment(session: Session, user_id: uuid.UUID, post_id: uuid.UUID, comment_in: CommentCreate):
    comment = Comment.model_validate(comment_in,update={"owner_id": user_id,"post_id":post_id})
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


def update_comment(session: Session, comment: Comment, update_in: CommentUpdate) -> Comment:
    update_data = update_in.model_dump(exclude_unset=True)
    comment.sqlmodel_update(update_data)
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment

def delete_comment(session: Session, comment: Comment):
    session.delete(comment)
    session.commit()
    return "Comment was successfully deleted"