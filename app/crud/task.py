from datetime import datetime

from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.models.tasks import Task, TaskActivity, TaskComment
from app.schemas.tasks import SortOrder, TaskCommentCreate, TaskCreate, TaskPriority, TaskSortBy, TaskStatus, TaskUpdate
from app.models.projectMember import ProjectMember

# 根据id搜索任务
def get_task_by_id(db: Session, task_id: int):
    return db.get(Task, task_id)

# 获取列表
def list_tasks_for_user(
               db: Session,
               user_id: int,
               project_id: int | None = None,
               status: TaskStatus | None = None,
               priority: TaskPriority | None = None,
               assignee_id: int | None = None,
               creator_id: int | None = None,
               due_date_from: datetime | None = None,
               due_date_to: datetime | None = None,
               sort_by: TaskSortBy = TaskSortBy.created_at,
               sort_order: SortOrder = SortOrder.desc,
               skip: int = 0, 
               limit: int = 10
               ) -> list[Task]:
    # 创建查询工具，真正启动数据库查询在 scalars
    # 获取对应用户的任务列表。 不要all
    stmt = (
        select(Task)
        .join(ProjectMember, ProjectMember.project_id == Task.project_id)
        .where(ProjectMember.user_id == user_id)
        )
    if project_id is not None:
        stmt = stmt.where(Task.project_id == project_id)
    if status is not None:
        stmt = stmt.where(Task.status == status)
    if priority is not None:
        stmt = stmt.where(Task.priority == priority)
    if assignee_id is not None:
        stmt = stmt.where(Task.assignee_id == assignee_id)
    if creator_id is not None:
        stmt = stmt.where(Task.creator_id == creator_id)
    if due_date_from is not None:
        stmt = stmt.where(Task.due_date >= due_date_from)
    if due_date_to is not None:
        stmt = stmt.where(Task.due_date <= due_date_to)

    sort_column = getattr(Task, sort_by.value)
    stmt = stmt.order_by(asc(sort_column) if sort_order == SortOrder.asc else desc(sort_column), desc(Task.id))
    stmt = stmt.offset(skip).limit(limit)
    return db.scalars(stmt).all()

# 创建任务
def create_task(db: Session, task_create: TaskCreate, creator_id: int):
    task = Task(
        **task_create.model_dump(),
        creator_id=creator_id,
    )
    db.add(task)
    db.flush()
    db.refresh(task)
    return task

# 更新任务
def update_task(db: Session, task: Task, task_update: TaskUpdate):
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def create_comment(db: Session, task_id: int, comment_create: TaskCommentCreate, author_id: int):
    comment = TaskComment(
        task_id=task_id,
        author_id=author_id,
        content=comment_create.content,
    )
    db.add(comment)
    db.flush()
    return comment


def list_comments(db: Session, task_id: int, skip: int = 0, limit: int = 20):
    stmt = (
        select(TaskComment)
        .where(TaskComment.task_id == task_id)
        .order_by(asc(TaskComment.created_at), asc(TaskComment.id))
        .offset(skip)
        .limit(limit)
    )
    return db.scalars(stmt).all()


def create_activity(
    db: Session,
    task_id: int,
    actor_id: int,
    action: str,
    field: str | None = None,
    old_value: str | None = None,
    new_value: str | None = None,
):
    activity = TaskActivity(
        task_id=task_id,
        actor_id=actor_id,
        action=action,
        field=field,
        old_value=old_value,
        new_value=new_value,
    )
    db.add(activity)
    db.flush()
    return activity


def list_activities(db: Session, task_id: int, skip: int = 0, limit: int = 50):
    stmt = (
        select(TaskActivity)
        .where(TaskActivity.task_id == task_id)
        .order_by(desc(TaskActivity.created_at), desc(TaskActivity.id))
        .offset(skip)
        .limit(limit)
    )
    return db.scalars(stmt).all()

# 删除任务
def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()
