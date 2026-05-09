from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.user import get_user_list
from app.db.deps import get_db
from app.models.user import User
from app.schemas.user import userResponse

router = APIRouter(
    prefix='/user',
    tags=['user']
)

@router.get('/me', response_model=userResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get('/list', response_model=list[userResponse])
def list_users(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_list(db, skip, limit)
