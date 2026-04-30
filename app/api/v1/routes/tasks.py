from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.schemas.tasks import TaskResponse, TaskUpdate, taskInfo
from ....data.taks import tasks
from app.db.deps import get_db
from app.models.tasks import Task

router = APIRouter(prefix='/tasks', tags=['tasks'])

# 获取任务列表
@router.get('/tasks', response_model=list[TaskResponse], summary="获取任务列表")
def tasks_list(status: str | None = None, db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    stmt = select(Task)
    if status is not None:
        stmt = stmt.where(Task.status == status)
    stmt = stmt.offset(skip).limit(limit)
    return db.scalars(stmt).all()


# 获取指定id
@router.get("/tasks/{id}", response_model=TaskResponse)
def by_id_to_task(id: int, db: Session = Depends(get_db)):
    task = db.get(Task, id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'msg':"没有数据"})
    return task


# 创建数据
@router.post('/tasks', response_model=TaskResponse, summary="创建任务", description='创建一条新任务')
def create_task(item: taskInfo, db: Session = Depends(get_db)):
    task = Task(**item.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


# 修改函数
@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    # 自动利用主键去搜索
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=201, detail="Task not found")
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


# 删除指定id
@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=201, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return { 'detail':'删除成功' }
