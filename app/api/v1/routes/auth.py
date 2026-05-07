from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.crud.user import get_user_by_email, get_user_by_username, create_user
from app.schemas.user import userCreate, userResponse
from app.db.deps import get_db
from app.schemas.token import Token
from app.core.security import verify_password, create_access_token




router = APIRouter(prefix='/auth', tags=['auth'])

# 注册账号
@router.post('/register', response_model=userResponse, status_code=status.HTTP_201_CREATED)
def register(user_create: userCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user_create.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"msg": "Email already registered"})
    if get_user_by_username(db, user_create.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"msg": "Username already registered"})
    return create_user(db, user_create)

# 登录账号
@router.post("/login", response_model=Token)
def login(formData:OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, formData.username)

    if user is None or not verify_password(formData.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"msg":"Invalid username or password"},
        )
    return Token(access_token=create_access_token(subject=str(user.id)))