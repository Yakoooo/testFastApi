from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import userResponse

router = APIRouter(
    prefix='/user',
    tags=['user']
)

@router.get('/me', response_model=userResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user