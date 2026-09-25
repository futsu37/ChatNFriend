from sqlmodel import create_engine, Session

from backend.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

def db_init(session: Session) -> None:
    pass