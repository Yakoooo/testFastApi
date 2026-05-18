from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectTaskStats(BaseModel):
    total: int = 0
    by_status: dict[str, int] = Field(default_factory=dict)
    by_priority: dict[str, int] = Field(default_factory=dict)
    overdue: int = 0


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    owner_id: int
    created_at: datetime
    updated_at: datetime
    task_count: int
    task_stats: ProjectTaskStats = Field(default_factory=ProjectTaskStats)

class ProjectMemberCreate(BaseModel):
    user_list: list[int] = Field(min_length=1)


class ProjectMemberAddResponse(BaseModel):
    added_user_ids: list[int]
    skipped_user_ids: list[int]


project_member_list = ProjectMemberCreate
