from fastapi import HTTPException

from app.crud import project as crud_project
from app.crud import project_member as crud_project_member


def require_project_member(db, project_id, user_id):
    project = crud_project.get_project_by_id(db, project_id)

    if project is None:
        raise HTTPException(404, "Project not found")

    member = crud_project_member.get_member(db, project_id, user_id)

    if member is None:
        raise HTTPException(403, "Not a project member")

    return project


def require_project_owner(db, project_id, user_id):
    project = crud_project.get_project_by_id(db, project_id)

    if project is None:
        raise HTTPException(404, "Project not found")

    member = crud_project_member.get_member(db, project_id, user_id)

    if member is None or member.role != "owner":
        raise HTTPException(403, "Only project owner can do this")

    return project
