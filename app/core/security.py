from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
import jwt

from app.core.config import settings

# 鉴权1 明文密码转化
# 获取hash推荐配置
password_hash = PasswordHash.recommended() 

def hash_password(password: str) -> str:
    return password_hash.hash(password)

# 哈希不可逆，工具比较
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

# 生成token
def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, settings.algorithm)