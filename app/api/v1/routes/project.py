from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import project as crud_project
from app.db.deps import get_db
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

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
):
    return crud_project.create_project(db, project_create)


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
