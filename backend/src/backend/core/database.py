from sqlmodel import Session, create_engine

from backend.core.config import settings
from backend.crud.user import create_user, get_user_by_username
from backend.schemas.user import UserCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

def init_db(session: Session) -> None:
    super_user = get_user_by_username(session,settings.FIRST_SUPERUSER_USERNAME)
    
    if not super_user:
        user_in = UserCreate(
            username=settings.FIRST_SUPERUSER_USERNAME,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True
        )
        create_user(session,user_in)