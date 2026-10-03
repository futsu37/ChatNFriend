import uuid

from fastapi import APIRouter, HTTPException

from backend.api.deps import CurrentUser, SessionDep
from backend.crud import comment
from backend.models import Comment
from backend.schemas.comment import CommentPublic, CommentsPublic, CommentUpdate

router = APIRouter(tags=["Comments"], prefix="/comments")

@router.get("/", response_model=CommentsPublic)
def read_comments(
    session: SessionDep, 
    current_user: CurrentUser,
    limit: int = 100,
    offset: int = 0):
    
    if current_user.is_superuser:
            comments_db, count = comment.get_comments(session,limit,offset)
    else:
            comments_db, count = comment.get_user_comments(session,current_user.id,limit,offset)
    
    return CommentsPublic(data=comments_db,count=count)


@router.post("/id/{comment_id}",response_model=CommentPublic)
def update_comment(
    session: SessionDep, 
    current_user: CurrentUser,
    comment_id: uuid.UUID,
    comment_in: CommentUpdate):
    existing_comment = session.get(Comment, comment_id)
    if not existing_comment:
        raise HTTPException(status_code=404,detail="Comment not found")
    if current_user.id != existing_comment.owner_id:
        raise HTTPException(status_code=403,detail="You can only update your comments")
    return comment.update_comment(session,existing_comment,comment_in)

@router.delete("/id/{comment_id}")
def delete_comment(
    session: SessionDep, 
    current_user: CurrentUser, 
    comment_id: uuid.UUID):
    existing_comment = session.get(Comment, comment_id)
    if not existing_comment:
        raise HTTPException(status_code=404,detail="Comment not found")
    if not current_user.is_superuser and current_user.id != existing_comment.owner_id:
        raise HTTPException(status_code=403,detail="You can only delete your comments")
    return comment.delete_comment(session, existing_comment)