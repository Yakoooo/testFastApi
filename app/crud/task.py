from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tasks import Task
from app.schemas.tasks import TaskCreate, TaskUpdate

# 根据id搜索任务
def get_task_by_id(db: Session, task_id: int):
    return db.get(Task, task_id)

# 获取列表
def list_tasks(db: Session,
               status: str | None = None,
               skip: int = 0, 
               limit: int = 10
               ) -> list[Task]:
    # 创建查询工具，真正启动数据库查询在 scalars
    stmt = select(Task)
    if status is not None:
        stmt = stmt.where(Task.status == status)
    stmt = stmt.offset(skip).limit(limit)
    return db.scalars(stmt).all()

# 创建任务
def create_task(db: Session, task_create: TaskCreate):
    task = Task(**task_create.model_dump())
    db.add(task)
    db.commit()
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

# 删除任务
def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()