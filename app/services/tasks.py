from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import task as crud_task
from app.models.tasks import Task
from app.schemas.tasks import (
    SortOrder,
    TaskCommentCreate,
    TaskCreate,
    TaskPriority,
    TaskSortBy,
    TaskStatus,
    TaskUpdate,
)


ALLOWED_STATUS_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.todo: {TaskStatus.in_progress, TaskStatus.canceled},
    TaskStatus.in_progress: {TaskStatus.todo, TaskStatus.review, TaskStatus.done, TaskStatus.canceled},
    TaskStatus.review: {TaskStatus.in_progress, TaskStatus.done, TaskStatus.canceled},
    TaskStatus.done: {TaskStatus.in_progress},
    TaskStatus.canceled: {TaskStatus.todo},
}


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
    limit: int = 10,
):
    if due_date_from is not None and due_date_to is not None and due_date_from > due_date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "due_date_from 不能晚于 due_date_to"},
        )

    return crud_task.list_tasks_for_user(
        db=db,
        user_id=user_id,
        project_id=project_id,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        creator_id=creator_id,
        due_date_from=due_date_from,
        due_date_to=due_date_to,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )


def create_task(db: Session, task_create: TaskCreate, creator_id: int):
    task = crud_task.create_task(db, task_create, creator_id)
    crud_task.create_activity(
        db,
        task_id=task.id,
        actor_id=creator_id,
        action="created",
    )
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: Task, task_update: TaskUpdate, actor_id: int):
    update_data = task_update.model_dump(exclude_unset=True)
    if not update_data:
        return task
    _require_required_fields_not_null(update_data)

    new_status = update_data.get("status")
    if new_status is not None:
        _require_valid_status_transition(_normalize_status(task.status), new_status)

    changes = _collect_changes(task, update_data)
    for field, value in update_data.items():
        setattr(task, field, value)

    for field, old_value, new_value in changes:
        crud_task.create_activity(
            db,
            task_id=task.id,
            actor_id=actor_id,
            action="status_changed" if field == "status" else "updated",
            field=field,
            old_value=_stringify_activity_value(old_value),
            new_value=_stringify_activity_value(new_value),
        )

    db.commit()
    db.refresh(task)
    return task


def create_comment(db: Session, task_id: int, comment_create: TaskCommentCreate, author_id: int):
    comment = crud_task.create_comment(db, task_id, comment_create, author_id)
    crud_task.create_activity(
        db,
        task_id=task_id,
        actor_id=author_id,
        action="commented",
        field="comment",
        new_value=comment.content,
    )
    db.commit()
    db.refresh(comment)
    return comment


def _collect_changes(task: Task, update_data: dict[str, Any]):
    changes: list[tuple[str, Any, Any]] = []
    for field, new_value in update_data.items():
        old_value = getattr(task, field)
        if _normalize_activity_value(old_value) == _normalize_activity_value(new_value):
            continue
        changes.append((field, old_value, new_value))
    return changes


def _require_required_fields_not_null(update_data: dict[str, Any]) -> None:
    empty_fields = [
        field
        for field in ("title", "status", "priority")
        if field in update_data and update_data[field] is None
    ]
    if not empty_fields:
        return
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"msg": "字段不能为空", "fields": empty_fields},
    )


def _require_valid_status_transition(old_status: TaskStatus, new_status: TaskStatus) -> None:
    if old_status == new_status:
        return
    allowed_statuses = ALLOWED_STATUS_TRANSITIONS.get(old_status, set())
    if new_status in allowed_statuses:
        return
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "msg": "非法任务状态流转",
            "from": old_status.value,
            "to": new_status.value,
        },
    )


def _normalize_status(value: TaskStatus | str) -> TaskStatus:
    if isinstance(value, TaskStatus):
        return value
    return TaskStatus(value)


def _normalize_activity_value(value: Any):
    if isinstance(value, (TaskStatus, TaskPriority)):
        return value.value
    return value


def _stringify_activity_value(value: Any) -> str | None:
    value = _normalize_activity_value(value)
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)
