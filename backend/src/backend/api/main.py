from fastapi import APIRouter

from backend.api.routes import (
    comments,
    friendships,
    login,
    messages,
    posts,
    rooms,
    users,
    utils,
    websockets,
)
from backend.core.config import settings

api_router = APIRouter()
if settings.DEVELOPER_MODE:
    api_router.include_router(utils.router)
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(posts.router)
api_router.include_router(comments.router)
api_router.include_router(friendships.router)
api_router.include_router(rooms.router)
api_router.include_router(messages.router)
api_router.include_router(websockets.router)