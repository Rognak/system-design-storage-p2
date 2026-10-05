import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Project, ProjectMember, User
from ..schemas import ProjectCreate, ProjectRead

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    owner = db.get(User, payload.owner_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="owner not found")

    project = Project(**payload.model_dump())
    db.add(project)
    db.flush()

    # Владелец автоматически становится участником проекта.
    db.add(ProjectMember(project_id=project.id, user_id=payload.owner_id))
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(owner_id: uuid.UUID | None = None, db: Session = Depends(get_db)):
    stmt = select(Project).where(Project.is_deleted.is_(False))
    if owner_id is not None:
        stmt = stmt.where(Project.owner_id == owner_id)
    return db.scalars(stmt.order_by(Project.created_at.desc())).all()


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    project.is_deleted = True
    db.commit()
