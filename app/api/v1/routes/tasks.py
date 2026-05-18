from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud import task as crud_tasks, project as crud_project
from app.schemas.tasks import TaskResponse, TaskUpdate, TaskCreate
from app.db.deps import get_db
from app.models.user import User
from app.services.project_permission import (
    require_assignee_project_member,
    require_project_member,
    require_task_owner_or_creator,
    require_task_project_member,
)

router = APIRouter(prefix='/tasks', tags=['tasks'])

# 获取任务列表
# 只返回当前用户参与项目里面的任务
@router.get('', response_model=list[TaskResponse], summary="获取任务列表")
def tasks_list(
    status: str | None = None, 
    current_user:User = Depends(get_current_user),
    db: Session = Depends(get_db), 
    skip: int = 0, limit: int = 10):

    # list_tasks_for_user 根据用户返回对应任务
    res = crud_tasks.list_tasks_for_user(db, current_user.id, status,  skip, limit)
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
    
    return crud_tasks.create_task(db, item, creator_id=current_user.id)


# 修改函数
@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int, 
    task_update: TaskUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ):
    task = require_task_owner_or_creator(db, task_id, current_user.id)
    require_assignee_project_member(db, task.project_id, task_update.assignee_id)

    return crud_tasks.update_task(db, task, task_update)


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
