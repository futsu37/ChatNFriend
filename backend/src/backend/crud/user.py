
from sqlmodel import Session, select

from backend.core.security import get_hashed_password
from backend.models import User
from backend.schemas.user import UserCreate


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