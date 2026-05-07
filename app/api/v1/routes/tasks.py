from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud import task as crud_tasks, project as crud_project
from app.schemas.tasks import TaskResponse, TaskUpdate, TaskCreate
from app.db.deps import get_db
from app.models.user import User

router = APIRouter(prefix='/tasks', tags=['tasks'])

# 获取任务列表
@router.get('/tasks', response_model=list[TaskResponse], summary="获取任务列表")
def tasks_list(status: str | None = None, db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    res = crud_tasks.list_tasks(db, status, skip, limit)
    return res


# 获取指定id
@router.get("/tasks/{id}", response_model=TaskResponse)
def by_id_to_task(id: int, db: Session = Depends(get_db)):
    task = crud_tasks.get_task_by_id(db, id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'msg':"没有数据"})
    return task


# 创建数据
@router.post('/tasks', response_model=TaskResponse, summary="创建任务", description='创建一条新任务')
def create_task(
    item: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = crud_project.get_project_by_id(db, item.project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'msg':"项目不存在"})
    task = crud_tasks.create_task(db, item, creator_id=current_user.id)
    return task


# 修改函数
@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    # 自动利用主键去搜索
    task = crud_tasks.get_task_by_id(db, task_id)
    if task is None:
        raise HTTPException(status_code=201, detail="Task not found")
    task = crud_tasks.update_task(db, task, task_update)
    return task


# 删除指定id
@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = crud_tasks.get_task_by_id(db, task_id)
    if task is None:
        raise HTTPException(status_code=201, detail="Task not found")
    crud_tasks.delete_task(db, task)
    return { 'detail':'删除成功' }
