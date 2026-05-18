from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud import project as crud_project
from app.crud import project_member as crud_project_member
from app.crud import user as curd_user
from app.db.deps import get_db
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectMemberAddResponse,
    ProjectMemberCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.schemas.user import userResponse
from app.services.project_permission import require_project_member, require_project_owner

router = APIRouter(prefix="/projects", tags=["projects"])


# 获取用户相关项目列表
@router.get("/", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
):
    return crud_project.list_projects(db, current_user.id, skip, limit)

# 根据项目id获取项目信息
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return require_project_member(db, project_id, current_user.id)



@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    project_create: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud_project.create_project(db, project_create, owner_id=current_user.id)


# 更新任务信息
@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = require_project_owner(db, project_id, current_user.id)
    return crud_project.update_project(db, project, project_update)


# 删除任务
@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = require_project_owner(db, project_id, current_user.id)
    crud_project.delete_project(db, project)
    return


# 添加成员
@router.post(
    "/{project_id}/members",
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


# 查看项目成员
@router.get("/{project_id}/members", response_model=list[userResponse])
def get_members_by_id(project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    # GET 查看成员：项目成员即可
    require_project_member(db, project_id, current_user.id)
    # 搜索是否存在项目
    return crud_project_member.get_member_by_project_id(db, project_id)
