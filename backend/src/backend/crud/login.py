from sqlmodel import Session

from backend.core.security import verify
from backend.crud.user import get_user_by_username
from backend.models import User


def authenticate(session: Session, password: str, username: str) -> User | None:
    user = get_user_by_username(session,username) 
    if user is None:
        return None
    verified, new_password = verify(password,user.hashed_password)
    if not verified:
        return None
    if new_password:
        user.hashed_password = new_password
        session.add(user)
        session.commit()
        session.refresh(user)
    return user