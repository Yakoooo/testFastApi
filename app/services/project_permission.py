from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import project as crud_project
from app.crud import project_member as crud_project_member
from app.crud import task as crud_task


# 检查项目是否有该成员
def require_project_member(db, project_id, user_id):
    project = crud_project.get_project_by_id(db, project_id)

    if project is None:
        raise HTTPException(404, "Project not found")

    member = crud_project_member.get_member(db, project_id, user_id)

    if member is None:
        raise HTTPException(403, "Not a project member")

    return project



# 检查是否是项目拥有者
def require_project_owner(db, project_id, user_id):
    project = crud_project.get_project_by_id(db, project_id)

    if project is None:
        raise HTTPException(404, "Project not found")

    member = crud_project_member.get_member(db, project_id, user_id)

    if member is None or member.role != "owner":
        raise HTTPException(403, "Only project owner can do this")

    return project


# 检查任务负责人是否是项目成员
def require_assignee_project_member(
    db: Session,
    project_id: int,
    assignee_id: int | None,
) -> None:
    if assignee_id is None:
        return

    require_project_member(db, project_id, assignee_id)


# 判断当前用户是不是这个任务所属项目的成员
def require_task_project_member(db: Session, task_id: int, user_id: int):
    task = crud_task.get_task_by_id(db, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "没找到任务"},
        )

    require_project_member(db, task.project_id, user_id)
    return task

# 通过任务id检查是否为拥有者或者创建者
def require_task_owner_or_creator(db: Session, task_id: int, user_id: int):
    task = crud_task.get_task_by_id(db, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "没找到任务"},
        )

    if task.creator_id == user_id:
        return task

    member = crud_project_member.get_member(db, task.project_id, user_id)
    if member is not None and member.role == "owner":
        return task

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"msg": "只有项目拥有者或任务创建者可以操作"},
    )
