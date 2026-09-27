import uuid

from fastapi import APIRouter, Depends, HTTPException

from backend.api.deps import CurrentUser, SessionDep, get_active_superuser
from backend.core.security import get_hashed_password
from backend.crud import user
from backend.models import User
from backend.schemas.user import (
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)

router = APIRouter(tags=["Users"],prefix="/users")

@router.get(
    "/",
    dependencies=[Depends(get_active_superuser)],
    response_model=UsersPublic)
def read_users(session: SessionDep, offset: int = 0, limit: int = 100) -> UsersPublic:
    users_db, count = user.get_users(session,limit,offset)

    users = [UserPublic.model_validate(user) for user in users_db]
    return UsersPublic(data=users,count=count)

@router.get('/me',response_model=UserPublic)
def read_user_me(current_user: CurrentUser):
    return current_user
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
def update_user_me(session: SessionDep, current_user:CurrentUser, user_update: UserUpdateMe):
    if user_update.username and user.get_user_by_username(session, user_update.username):
        raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system",
            )
    update_data = user_update.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(update_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user
@router.delete("/me")
def delete_user_me(session: SessionDep, current_user: CurrentUser):
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    return user.delete_user(session, current_user)
@router.get("/id/{user_id}", response_model=UserPublic)
def find_user_by_id(session: SessionDep, user_id: uuid.UUID):
    existing_user = session.get(User,user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User with this id does not exist")
    return existing_user
@router.get("/username/{username}", response_model=UserPublic)
def find_user_by_username(session: SessionDep, username: str):
    existing_user = user.get_user_by_username(session,username)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User with this username does not exist")
    return existing_user
@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_active_superuser)],
    response_model=UserPublic)
def update_user_by_id(
    session: SessionDep, 
    user_id: uuid.UUID, 
    user_update: UserUpdate):
    existing_user = session.get(User, user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User with this id does not exist")
    if user_update.username and user.get_user_by_username(session,user_update.username):
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    update_data = user_update.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in update_data:
        password = update_data["password"]
        hashed_password = get_hashed_password(password)
        extra_data["hashed_password"] = hashed_password
    existing_user.sqlmodel_update(update_data,update=extra_data)
    session.add(existing_user)
    session.commit()
    session.refresh(existing_user)
    return existing_user
@router.delete(
    "/{user_id}",
    dependencies=[Depends(get_active_superuser)])
def delete_user_by_id(session: SessionDep, user_id: uuid.UUID):
    existing_user = session.get(User, user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User with this id does not exist")
    if existing_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    return user.delete_user(session,existing_user)
    
    
