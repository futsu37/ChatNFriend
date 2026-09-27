import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, select

from backend.api.deps import CurrentUser, SessionDep, get_active_superuser
from backend.models import Post
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
        posts_statement = select(Post).order_by(col(Post.created_at).desc()).offset(offset).limit(limit)
        posts_db = session.exec(posts_statement).all()
    else:
        posts_statement = select(Post).where(Post.owner_id == current_user.id).order_by(col(Post.created_at).desc()).offset(offset).limit(limit)
        posts_db = session.exec(posts_statement).all()
    count = posts_db.__len__()
    return PostsPublic(data=posts_db,count=count)

@router.get("/id/{post_id}", response_model=PostPublic)
def read_post(session: SessionDep, post_id: uuid.UUID):
    existing_post = session.get(Post,post_id)
    if not existing_post:
        raise HTTPException(status_code=404,detail="Post not found")
    return existing_post

@router.post("/",response_model=PostPublic)
def create_post(session: SessionDep,current_user: CurrentUser, post_in: PostCreate):
    post = Post.model_validate(post_in, update={"owner_id": current_user.id})
    session.add(post)
    session.commit()
    session.refresh(post)
    return post

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
    update_data = update_in.model_dump(exclude_unset=True)
    existing_post.sqlmodel_update(update_data)
    session.add(existing_post)
    session.commit()
    session.refresh(existing_post)
    return existing_post
@router.patch("/id/{post_id}",dependencies=[Depends(get_active_superuser)],response_model=PostPublic)
def update_post(
    session: SessionDep, 
    post_id: uuid.UUID,
    update_in: PostUpdate):
    existing_post = session.get(Post, post_id)
    if not existing_post:
        raise HTTPException(status_code=404,detail="Post not found")
    update_data = update_in.model_dump(exclude_unset=True)
    existing_post.sqlmodel_update(update_data)
    session.add(existing_post)
    session.commit()
    session.refresh(existing_post)
    return existing_post

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
    session.delete(existing_post)
    session.commit()
    return "Post was successfully deleted"

