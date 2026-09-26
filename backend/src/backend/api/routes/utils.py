import uuid

from fastapi import APIRouter

from backend.api.deps import SessionDep
from backend.crud.user import create_user
from backend.schemas.user import UserCreate, UsersPublic

router = APIRouter(tags=["Dev utils"], prefix="/utils")

@router.post("/", response_model=UsersPublic)
def create_dummy(session: SessionDep, amount: int = 1):
    dummies = []
    for _ in range(amount):
        username = "Dummy" + str(uuid.uuid4())
        password = "Dummy123"
        dummy_in = UserCreate(username=username,password=password)
        dummies.append(create_user(session,dummy_in))
    return UsersPublic(data=dummies,count=dummies.__len__())