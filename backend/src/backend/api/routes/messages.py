import uuid

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.api.deps import CurrentUser, SessionDep, get_active_superuser
from backend.events.redis_events import publish_chat_event
from backend.models import Message
from backend.schemas.message import MessagePublic, MessageUpdate
from backend.schemas.redis import RedisEvent

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
async def redact_message(
    session: SessionDep,
    request: Request,
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
    await publish_chat_event(
        request.app.state.redis,
        RedisEvent(
            event="message_updated",
            room_id=existing_message.room_id,
            message=MessagePublic.model_validate(existing_message),
        ),
    )
    return existing_message

@router.delete("/id/{message_id}",)
async def delete_message(
    session: SessionDep,
    request: Request,
    current_user: CurrentUser,
    message_id: uuid.UUID,
):
    existing_message = session.get(Message,message_id)
    if not existing_message:
        raise HTTPException(status_code=404,detail="Message not found")
    if existing_message.sender_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403,detail="You can only delete your own messages")
    room_id = existing_message.room_id
    session.delete(existing_message)
    session.commit()
    await publish_chat_event(
        request.app.state.redis,
        RedisEvent(
            event="message_deleted",
            room_id=room_id,
            message_id=message_id,
        ),
    )
    return "Message was successfully deleted"
