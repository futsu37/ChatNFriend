from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlmodel import Session

from backend.core.config import settings
from backend.core.database import engine
from backend.core.security import ALGORITHM
from backend.models import User
from backend.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

def get_db():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session,Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]

def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,algorithms=[ALGORITHM,])
        token_data = TokenPayload.model_validate(payload)
        user = session.get(User, token_data.sub)
    except jwt.InvalidTokenError, ValidationError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

def get_active_superuser(current_user: CurrentUser):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="The user does not has enough privileges")
    return current_user