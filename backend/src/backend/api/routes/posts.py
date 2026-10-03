import uuid

from fastapi import APIRouter, Depends, HTTPException

from backend.api.deps import CurrentUser, SessionDep, get_active_superuser
from backend.crud import comment, post
from backend.models import Post
from backend.schemas.comment import CommentCreate, CommentPublic
from backend.schemas.post import (
    PostCreate,
    PostPublic,
    PostsPublic,
    PostUpdate,
    PostUpdateMe,
)

router = APIRouter(tags=["Posts"], prefix="/posts")

@router.get("/", response_model=PostsPublic)
def read_posts(
    session: SessionDep, 
    current_user: CurrentUser, 
    limit: int = 100,
    offset: int = 0) -> PostsPublic:
    
    if current_user.is_superuser:
        posts_db, count = post.get_posts(session,limit,offset)
    else:
        posts_db, count = post.get_user_posts(session,current_user.id,limit,offset)
    return PostsPublic(data=posts_db,count=count)

@router.get("/id/{post_id}", response_model=PostPublic)
def read_post(session: SessionDep, post_id: uuid.UUID):
    existing_post = session.get(Post,post_id)
    if not existing_post:
        raise HTTPException(status_code=404,detail="Post not found")
    return existing_post

@router.post("/",response_model=PostPublic)
def create_post(session: SessionDep,current_user: CurrentUser, post_in: PostCreate):
    return post.create_post(session,current_user,post_in)

@router.patch("/me/id/{post_id}",response_model=PostPublic)
def update_post_me(
    session: SessionDep, 
    current_user:CurrentUser,
    post_id: uuid.UUID,
    update_in: PostUpdateMe):
    existing_post = session.get(Post, post_id)
    if not existing_post:
        raise HTTPException(status_code=404,detail="Post not found")
    if current_user.id != existing_post.owner_id:
        raise HTTPException(status_code=403,detail="You can only update your posts")
    return post.update_post(session,existing_post,update_in)
@router.patch("/id/{post_id}",dependencies=[Depends(get_active_superuser)],response_model=PostPublic)
def update_post(
    session: SessionDep, 
    post_id: uuid.UUID,
    update_in: PostUpdate):
    existing_post = session.get(Post, post_id)
    if not existing_post:
        raise HTTPException(status_code=404,detail="Post not found")
    return post.update_post(session,existing_post,update_in)

@router.delete("/id/{post_id}")
def delete_post(
    session: SessionDep, 
    current_user: CurrentUser, 
    post_id: uuid.UUID):
    existing_post = session.get(Post, post_id)
    if not existing_post:
        raise HTTPException(status_code=404,detail="Post not found")
    if not current_user.is_superuser and current_user.id != existing_post.owner_id:
        raise HTTPException(status_code=403,detail="You can only delete your posts")
    return post.delete_post(session, existing_post)


@router.post("/id/{post_id}/comment",response_model=CommentPublic)
def create_comment(
    session: SessionDep, 
    current_user: CurrentUser,
    post_id: uuid.UUID,
    comment_in: CommentCreate):
    return comment.create_comment(session,current_user.id,post_id,comment_in)



