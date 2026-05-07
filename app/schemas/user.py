from pydantic import BaseModel, ConfigDict, EmailStr

from datetime import datetime


class userCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class userResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime