from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


# 根据id搜索项目
def get_project_by_id(db: Session, project_id: int):
    return db.get(Project, project_id)


# 获取项目列表
def list_projects(
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> list[Project]:
    stmt = select(Project).offset(skip).limit(limit)
    return db.scalars(stmt).all()


# 创建项目
def create_project(db: Session, project_create: ProjectCreate):
    project = Project(**project_create.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


# 更新项目
def update_project(db: Session, project: Project, project_update: ProjectUpdate):
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


# 删除项目
def delete_project(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()
