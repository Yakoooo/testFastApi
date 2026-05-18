from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud import task as crud_tasks
from app.db.deps import get_db
from app.models.user import User
from app.schemas.tasks import (
    SortOrder,
    TaskActivityResponse,
    TaskCommentCreate,
    TaskCommentResponse,
    TaskCreate,
    TaskPriority,
    TaskResponse,
    TaskSortBy,
    TaskStatus,
    TaskUpdate,
)
from app.services.project_permission import (
    require_assignee_project_member,
    require_project_member,
    require_task_owner_or_creator,
    require_task_project_member,
)
from app.services import tasks as task_service

router = APIRouter(prefix='/tasks', tags=['tasks'])

# 获取任务列表
# 只返回当前用户参与项目里面的任务
@router.get('', response_model=list[TaskResponse], summary="获取任务列表")
def tasks_list(
    project_id: int | None = None,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assignee_id: int | None = None,
    creator_id: int | None = None,
    due_date_from: datetime | None = None,
    due_date_to: datetime | None = None,
    sort_by: TaskSortBy = TaskSortBy.created_at,
    sort_order: SortOrder = SortOrder.desc,
    current_user:User = Depends(get_current_user),
    db: Session = Depends(get_db), 
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):

    # list_tasks_for_user 根据用户返回对应任务
    res = task_service.list_tasks_for_user(
        db=db,
        user_id=current_user.id,
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
    return res


# 根据指定id获取任务详细
@router.get("/{id}", response_model=TaskResponse)
def by_id_to_task(
    id: int, 
    db: Session = Depends(get_db),
    current_user:User = Depends(get_current_user),
    ):
    return require_task_project_member(db, id, current_user.id)


# 创建任务
@router.post('', response_model=TaskResponse, summary="创建任务", description='创建一条新任务')
def create_task(
    item: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_member(db, item.project_id, current_user.id)
    require_assignee_project_member(db, item.project_id, item.assignee_id)
    
    return task_service.create_task(db, item, creator_id=current_user.id)


# 修改函数
@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int, 
    task_update: TaskUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ):
    task = require_task_owner_or_creator(db, task_id, current_user.id)
    if "assignee_id" in task_update.model_fields_set:
        require_assignee_project_member(db, task.project_id, task_update.assignee_id)

    return task_service.update_task(db, task, task_update, actor_id=current_user.id)


@router.get("/{task_id}/comments", response_model=list[TaskCommentResponse], summary="获取任务评论")
def list_task_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    require_task_project_member(db, task_id, current_user.id)
    return crud_tasks.list_comments(db, task_id, skip, limit)


@router.post("/{task_id}/comments", response_model=TaskCommentResponse, status_code=status.HTTP_201_CREATED, summary="添加任务评论")
def create_task_comment(
    task_id: int,
    comment_create: TaskCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_task_project_member(db, task_id, current_user.id)
    return task_service.create_comment(db, task_id, comment_create, author_id=current_user.id)


@router.get("/{task_id}/activities", response_model=list[TaskActivityResponse], summary="获取任务活动日志")
def list_task_activities(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    require_task_project_member(db, task_id, current_user.id)
    return crud_tasks.list_activities(db, task_id, skip, limit)


# 删除指定id
@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    task = require_task_owner_or_creator(db, task_id, current_user.id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    crud_tasks.delete_task(db, task)
    return { 'detail':'删除成功' }
