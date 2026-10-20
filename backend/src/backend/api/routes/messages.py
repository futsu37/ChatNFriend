import uuid

from fastapi import APIRouter, Depends, HTTPException

from backend.api.deps import CurrentUser, SessionDep, get_active_superuser
from backend.models import Message
from backend.schemas.message import MessagePublic, MessageUpdate

router = APIRouter(prefix="/messages",tags=["Messages"])

@router.get(
    "/id/{message_id}",
    dependencies=[Depends(get_active_superuser)],
    response_model=MessagePublic)
def read_message(session: SessionDep, message_id: uuid.UUID):
    existing_message = session.get(Message,message_id)
    if not existing_message:
        raise HTTPException(status_code=404,detail="Message not found")
    return MessagePublic.model_validate(existing_message)

@router.patch(
    "/id/{message_id}",
    response_model=MessagePublic)
def redact_message(
    session: SessionDep,
    current_user:CurrentUser, 
    message_id: uuid.UUID, 
    message_update: MessageUpdate):
    existing_message = session.get(Message,message_id)
    if not existing_message:
        raise HTTPException(status_code=404,detail="Message not found")
    if existing_message.sender_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403,detail="You can only redact your own messages")
    existing_message.sqlmodel_update(message_update.model_dump(exclude_unset=True))
    session.add(existing_message)
    session.commit()
    session.refresh(existing_message)
    return existing_message

@router.delete("/id/{message_id}",)
def delete_message(session: SessionDep,current_user:CurrentUser, message_id: uuid.UUID):
    existing_message = session.get(Message,message_id)
    if not existing_message:
        raise HTTPException(status_code=404,detail="Message not found")
    if existing_message.sender_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403,detail="You can only delete your own messages")
    session.delete(existing_message)
    session.commit()
    return "Message was successfully deleted"
