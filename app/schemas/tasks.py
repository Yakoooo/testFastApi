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


class TaskSortBy(str, Enum):
    created_at = "created_at"
    updated_at = "updated_at"
    due_date = "due_date"
    priority = "priority"
    status = "status"
    title = "title"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


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
    priority: TaskPriority | None = None
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


class TaskCommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class TaskCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    author_id: int
    content: str
    created_at: datetime
    updated_at: datetime


class TaskActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    actor_id: int
    action: str
    field: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    created_at: datetime
