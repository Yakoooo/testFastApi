from datetime import datetime

from pydantic import BaseModel, ConfigDict
from enum import Enum


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class taskInfo(BaseModel):
    title:str
    description: str | None = None
    status: TaskStatus = "todo"
    project_id: int


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    status: TaskStatus
    project_id: int
    created_at: datetime
    updated_at: datetime


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
