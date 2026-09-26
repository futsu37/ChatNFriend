from fastapi import APIRouter

from backend.api.routes import login, users, utils
from backend.core.config import settings

api_router = APIRouter()
if settings.DEVELOPER_MODE:
    api_router.include_router(utils.router)
api_router.include_router(login.router)
api_router.include_router(users.router)
