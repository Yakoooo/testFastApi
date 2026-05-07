from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import userCreate

# 根据邮箱获取用户
def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))
 
# 根据用户名查询
def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))

# 创建用户
def create_user(db: Session, user_create: userCreate) -> User:
    user = User(
        email=user_create.email,
        username=user_create.username,
        hashed_password=hash_password(user_create.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user