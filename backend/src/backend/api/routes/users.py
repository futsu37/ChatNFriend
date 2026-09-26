from backend.models import User
from fastapi import APIRouter, Depends, HTTPException

from backend.api.deps import SessionDep, get_active_superuser, CurrentUser
from backend.crud import user
from backend.schemas.user import UserCreate, UserPublic, UserRegister, UsersPublic, UserUpdate

router = APIRouter(tags=["Users"],prefix="/users")

@router.get(
    "/",
    dependencies=[Depends(get_active_superuser)],
    response_model=UsersPublic)
def read_users(session: SessionDep, offset: int = 0, limit: int = 100) -> UsersPublic:
    users_db, count = user.get_users(session,limit,offset)

    users = [UserPublic.model_validate(user) for user in users_db]
    return UsersPublic(data=users,count=count)

@router.post("/signup",response_model=UserPublic)
def register(session: SessionDep, user_in: UserRegister):
    existing_user = user.get_user_by_username(session,user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this username already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    new_user = user.create_user(session,user_create)
    return new_user
@router.patch("/me", response_model=UserPublic)
def update_user_me(session: SessionDep, current_user:CurrentUser, user_update: UserUpdate):
    if user_update.username and user.get_user_by_username(session, user_update.username):
        raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system",
            )

    updated_user = user.update_user(session,current_user,user_update)
    return updated_user
@router.delete("/me")
def delete_user_me(session: SessionDep, current_user: CurrentUser):
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    session.delete(current_user)
    session.commit()
    return "User was successfully deleted"
    