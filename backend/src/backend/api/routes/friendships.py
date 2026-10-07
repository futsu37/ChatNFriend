import uuid

from fastapi import APIRouter, HTTPException

from backend.api.deps import CurrentUser, SessionDep
from backend.crud import friendship
from backend.models import Friendship, User
from backend.models.friendship import Status
from backend.schemas.friendship import (
    FriendshipCreate,
    FriendshipPublic,
    FriendshipsPublic,
    FriendshipUpdate,
)

router = APIRouter(prefix="/friendships", tags=["friendships"])

@router.post("/send/id/{receiver_id}",response_model=FriendshipPublic)
def send_friend_request(
    session: SessionDep, 
    current_user:CurrentUser,
    receiver_id: uuid.UUID):
    if receiver_id == current_user.id:
        raise HTTPException(status_code=403, detail="You cannot befriend yourself")
    existing_user = session.get(User,receiver_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing_friendship = friendship.get_existing_friendship(
        session=session,
        receiver_id=receiver_id,
        requestor_id=current_user.id)
    if existing_friendship and existing_friendship.status == Status.ACCEPTED:
        raise HTTPException(status_code=400, detail="You already friends with this user")
    if existing_friendship:
        raise HTTPException(status_code=403, detail="You cannot send a friend request to that user")
    
    friendship_in = FriendshipCreate(receiver_id=receiver_id,requestor_id=current_user.id)
    new_friendship = Friendship.model_validate(friendship_in)
    session.add(new_friendship)
    session.commit()
    session.refresh(new_friendship)
    return new_friendship

@router.get("/",response_model=FriendshipsPublic)
def get_friendships(
    session: SessionDep, 
    current_user: CurrentUser,
    limit: int = 10,
    offset: int = 0):
    if current_user.is_superuser:
        db_friendships, count = friendship.get_existing_friendships(session,limit,offset)
    else:
        db_friendships, count = friendship.get_user_friendships(session,current_user.id,limit,offset)
    friendship_list = [FriendshipPublic.model_validate(friendship) for friendship in db_friendships]
    return FriendshipsPublic(data=friendship_list,count=count)
@router.get("/friends/me",response_model=FriendshipsPublic)
def get_user_friends_me(
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = 10,
    offset: int = 0):
    db_friendships, count = friendship.get_user_friends(session,current_user.id,limit,offset)
    friendship_list = [FriendshipPublic.model_validate(friendship) for friendship in db_friendships]
    return FriendshipsPublic(data=friendship_list,count=count)

@router.get("/friends/id/{user_id}",response_model=FriendshipsPublic)
def get_user_friends(
    session: SessionDep, 
    user_id: uuid.UUID,
    limit: int = 10,
    offset: int = 0):
    db_friendships, count = friendship.get_user_friends(session,user_id,limit,offset)
    friendship_list = [FriendshipPublic.model_validate(friendship) for friendship in db_friendships]
    return FriendshipsPublic(data=friendship_list,count=count)

@router.patch("/accept/id/{friendship_id}",response_model=FriendshipPublic)
def accept_friendship(
    session: SessionDep, 
    current_user: CurrentUser,
    friendship_id: uuid.UUID):
    existing_friendship = session.get(Friendship,friendship_id)
    if not existing_friendship:
        raise HTTPException(status_code=404, detail="Friendship not found")
    if existing_friendship.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="You cannot do this")
    if existing_friendship.status == Status.ACCEPTED:
        raise HTTPException(status_code=400, detail="You already friends with this user")
    model_update = FriendshipUpdate(status=Status.ACCEPTED)
    existing_friendship.sqlmodel_update(model_update.model_dump(exclude_unset=True))
    session.add(existing_friendship)
    session.commit()
    session.refresh(existing_friendship)
    return existing_friendship
@router.delete("/remove/id/{friendship_id}")
def remove_friendship(
    session: SessionDep,
    current_user: CurrentUser,
    friendship_id: uuid.UUID):
    existing_friendship = session.get(Friendship,friendship_id)
    if not existing_friendship:
        raise HTTPException(status_code=404, detail="Friendship not found")
    if (existing_friendship.receiver_id != current_user.id 
    and existing_friendship.requestor_id != current_user.id):
        raise HTTPException(status_code=403, detail="You cannot do this")
    session.delete(existing_friendship)
    session.commit()
    return "Friendship was successfully deleted"