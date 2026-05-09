from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud import project as crud_project
from app.crud import project_member as crud_project_member
from app.db.deps import get_db
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectMemberAddResponse,
    ProjectMemberCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project_permission import require_project_owner

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/project", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
):
    return crud_project.list_projects(db, skip, limit)


@router.get("/project/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = crud_project.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.post("/project", response_model=ProjectResponse, status_code=201)
def create_project(
    project_create: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud_project.create_project(db, project_create, owner_id=current_user.id)


@router.put("/project/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = crud_project.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return crud_project.update_project(db, project, project_update)


@router.delete("/project/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = crud_project.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    crud_project.delete_project(db, project)
    return


# 添加成员
@router.post(
    "/project/{project_id}/members",
    response_model=ProjectMemberAddResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    project_id: int,
    member_create: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 校验是否存在项目和所有权
    require_project_owner(db, project_id, current_user.id)

    user_ids = list(dict.fromkeys(member_create.user_list))
    invalid_user_ids = [user_id for user_id in user_ids if db.get(User, user_id) is None]
    if invalid_user_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "用户不存在", "user_ids": invalid_user_ids},
        )

    added_user_ids: list[int] = []
    skipped_user_ids: list[int] = []

    for user_id in user_ids:
        existing_member = crud_project_member.get_member(db, project_id, user_id)
        if existing_member is not None:
            skipped_user_ids.append(user_id)
            continue

        crud_project_member.create_member(db, project_id, user_id)
        added_user_ids.append(user_id)

    db.commit()

    return ProjectMemberAddResponse(
        added_user_ids=added_user_ids,
        skipped_user_ids=skipped_user_ids,
    )


# 查看任务成员
@router.get("/project/{project_id}/members")
def get_members_by_id(project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    # 搜索是否存在项目
    project = require_project_owner(db, project_id, current_user.id)
    # 通过项目检索是否存在用户
    