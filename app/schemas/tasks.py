from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


# 枚举
# 任务状态
class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    review= "review"
    done = "done"
    canceled = 'canceled'
# 任务优先事项
class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

# 任务创建
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=20)
    description: str | None = None
    status: TaskStatus = TaskStatus.todo
    project_id: int
    priority: TaskPriority = TaskPriority.medium
    due_date: datetime | None = None
    assignee_id: int | None = None

# 任务更新
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority = TaskPriority.medium
    due_date: datetime | None = None
    assignee_id: int | None = None

# 任务状态更行
class TaskStatusUpdate(BaseModel):
    status: TaskStatus

# 任务请求体返回
class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None
    project_id: int
    creator_id: int
    assignee_id: int | None = None
    created_at: datetime
    updated_at: datetime


