from fastapi import APIRouter, Depends
from sqlmodel import col, func, select

from backend.api.deps import SessionDep, get_active_superuser
from backend.models import User
from backend.schemas.user import UserPublic, UsersPublic

router = APIRouter(tags=["Users"],prefix="/users")

@router.get(
    "/",
    dependencies=[Depends(get_active_superuser)])
def read_users(session: SessionDep, offset: int = 0, limit: int = 100) -> UsersPublic:
    statement_count = select(func.count()).select_from(User)
    count = session.exec(statement_count).one()
    statement_users = select(User).order_by(col(User.created_at).desc()).offset(offset).limit(limit)
    users_db = session.exec(statement_users).all()

    users = [UserPublic.model_validate(user) for user in users_db]
    return UsersPublic(data=users,count=count)