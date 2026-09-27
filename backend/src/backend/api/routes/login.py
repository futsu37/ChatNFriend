from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from backend.api.deps import SessionDep
from backend.core.security import create_access_token
from backend.crud.login import authenticate
from backend.schemas.token import Token

router = APIRouter(tags=["Login"])

@router.post("/login/access-token")
def get_access_token(
    session: SessionDep, 
    user_form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate(session,user_form.password,user_form.username)
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect password or username")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token = create_access_token(user.id)
    return Token(access_token=access_token) 