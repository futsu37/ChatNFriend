from collections.abc import Sequence

from sqlmodel import Session, col, func, select

from backend.core.security import get_hashed_password
from backend.models import User
from backend.schemas.user import UserCreate, UserUpdate


def get_user_by_username(session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()

def create_user(session: Session, create_form: UserCreate) -> User:
    user = User.model_validate(
        create_form,update={"hashed_password": get_hashed_password(create_form.password)})
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
def count_users(session: Session) -> int:
    statement_count = select(func.count()).select_from(User)
    return session.exec(statement_count).one()

def get_users(session: Session,limit: int = 100, offset: int = 0) -> tuple[Sequence[User],int]:
    statement_users = select(User).order_by(col(User.created_at).desc()).offset(offset).limit(limit)
    count = count_users(session)
    return session.exec(statement_users).all(), count

def delete_user(session: Session, user: User):
    session.delete(user)
    session.commit()
    return "User was successfully deleted"