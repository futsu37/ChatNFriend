import uuid

from sqlmodel import Session, and_, col, or_, select

from backend.models import Friendship
from backend.models.friendship import Status


def get_existing_friendship( *,
    session: Session, 
    receiver_id: uuid.UUID,
    requestor_id: uuid.UUID) -> Friendship | None:
    statement = select(Friendship).where(

        or_(
            and_(
                Friendship.receiver_id == receiver_id,
                Friendship.requestor_id == requestor_id
                ),
            and_(
                Friendship.requestor_id == receiver_id,
                Friendship.receiver_id == requestor_id
                )
            )
        )
    return session.exec(statement).first()

def get_user_friendships(
    session: Session,
    user_id: uuid.UUID,
    limit: int = 10,
    offset: int = 0):
    statement = select(Friendship).where(
        or_(
            Friendship.receiver_id == user_id,
            Friendship.requestor_id == user_id
            )
        ).order_by(col(Friendship.created_at).desc()).limit(limit).offset(offset)
    friendships_db = session.exec(statement).all()
    count = friendships_db.__len__()

    return friendships_db, count

def get_existing_friendships(
    session: Session,
    limit: int = 10,
    offset: int = 0):
    statement = select(Friendship).order_by(col(Friendship.created_at).desc()).limit(limit).offset(offset)
    all_friendships = session.exec(statement).all()
    count = all_friendships.__len__() 
    return all_friendships, count

def get_user_friends(
    session: Session,
    user_id: uuid.UUID,
    limit: int = 10,
    offset: int = 0):
    statement = select(Friendship).where(
        and_(or_(
            Friendship.receiver_id == user_id,
            Friendship.requestor_id == user_id
            ),Friendship.status == Status.ACCEPTED)
        ).order_by(col(Friendship.created_at).desc()).limit(limit).offset(offset)
    friendships_db = session.exec(statement).all()
    count = friendships_db.__len__()

    return friendships_db, count
