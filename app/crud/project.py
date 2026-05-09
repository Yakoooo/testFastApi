from sqlalchemy import delete, select, func
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.tasks import Task
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.models.projectMember import ProjectMember

# 根据id搜索项目
def get_project_by_id(db: Session, project_id: int):
    return db.get(Project, project_id)


# 获取项目列表
def list_projects(
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> list[Project]:
    # 加入左查询计算任务数量
    stmt = (
        select(Project, func.count(Task.id).label('task_count'))
        .outerjoin(Task, Task.project_id == Project.id)
        .group_by(Project.id)
        .offset(skip).limit(limit)
        )
    rows = db.execute(stmt).all()
    # 获取的元组需要组装
    return [ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        task_count=task_count
    )
    for project, task_count in rows]


# 创建项目
def create_project(db: Session, project_create: ProjectCreate, owner_id: int):
    project = Project(**project_create.model_dump(), owner_id=owner_id)
    db.add(project)
    # 添加权限控制，添加项目的时候添加用户关系表
    db.flush()
    member = ProjectMember(
        project_id = project.id,
        user_id = owner_id,
        role="owner"
    )
    db.add(member)

    db.commit()
    db.refresh(project)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        task_count=0
        )


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
    db.execute(delete(ProjectMember).where(ProjectMember.project_id == project.id))
    db.delete(project)
    db.commit()
