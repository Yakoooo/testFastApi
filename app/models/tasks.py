
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Enum
from datetime import datetime, UTC
from typing import TYPE_CHECKING

from app.db.base import Base
from app.schemas.tasks import TaskPriority, TaskStatus

if TYPE_CHECKING:
    from app.models.project import Project


# Task任务模型表
class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Enum(TaskStatus), nullable=True, index=True, default=TaskStatus.todo)
    priority: Mapped[str] = mapped_column(Enum(TaskPriority), nullable=True, index=True, default=TaskPriority.medium)
    due_date: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # 项目id
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False, index=True)
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")

    # 创作者和受让人
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
