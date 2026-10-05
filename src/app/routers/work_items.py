import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Comment, Project, User, WorkItem, WorkItemEstim, WorkItemStatus
from ..schemas import (
    CommentCreate,
    CommentRead,
    EstimationRead,
    EstimationUpsert,
    WorkItemCreate,
    WorkItemRead,
    WorkItemStatusUpdate,
)

router = APIRouter(prefix="/work-items", tags=["work-items"])


@router.post("", response_model=WorkItemRead, status_code=status.HTTP_201_CREATED)
def create_work_item(payload: WorkItemCreate, db: Session = Depends(get_db)):
    project = db.get(Project, payload.project_id)
    if project is None or project.is_deleted:
        raise HTTPException(status_code=404, detail="project not found")

    creator = db.get(User, payload.creator_id)
    if creator is None:
        raise HTTPException(status_code=404, detail="creator not found")

    item = WorkItem(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="human_id already exists in project")
    db.refresh(item)
    return item


@router.get("", response_model=list[WorkItemRead])
def list_work_items(
    project_id: uuid.UUID,
    status_filter: WorkItemStatus | None = Query(default=None, alias="status"),
    priority: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(WorkItem).where(WorkItem.project_id == project_id)
    if status_filter is not None:
        stmt = stmt.where(WorkItem.status == status_filter)
    if priority is not None:
        # PostgreSQL JSONB @> ; использует GIN индекс на extrafields.
        stmt = stmt.where(WorkItem.extrafields.contains({"priority": priority}))
    return db.scalars(stmt.order_by(WorkItem.created_at.desc())).all()


@router.patch("/{work_item_id}/status", response_model=WorkItemRead)
def update_status(work_item_id: uuid.UUID, payload: WorkItemStatusUpdate, db: Session = Depends(get_db)):
    item = db.get(WorkItem, work_item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="work item not found")
    item.status = payload.status
    db.commit()
    db.refresh(item)
    return item


@router.put("/{work_item_id}/estimation", response_model=EstimationRead)
def upsert_estimation(work_item_id: uuid.UUID, payload: EstimationUpsert, db: Session = Depends(get_db)):
    if db.get(WorkItem, work_item_id) is None:
        raise HTTPException(status_code=404, detail="work item not found")

    estimation = db.get(WorkItemEstim, work_item_id)
    if estimation is None:
        estimation = WorkItemEstim(work_item_id=work_item_id, **payload.model_dump())
        db.add(estimation)
    else:
        for key, value in payload.model_dump().items():
            setattr(estimation, key, value)

    db.commit()
    db.refresh(estimation)
    return estimation


@router.post("/{work_item_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(work_item_id: uuid.UUID, payload: CommentCreate, db: Session = Depends(get_db)):
    if db.get(WorkItem, work_item_id) is None:
        raise HTTPException(status_code=404, detail="work item not found")
    if db.get(User, payload.author_id) is None:
        raise HTTPException(status_code=404, detail="author not found")

    comment = Comment(work_item_id=work_item_id, **payload.model_dump())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/{work_item_id}/comments", response_model=list[CommentRead])
def list_comments(work_item_id: uuid.UUID, db: Session = Depends(get_db)):
    stmt = (
        select(Comment)
        .where(Comment.work_item_id == work_item_id)
        .order_by(Comment.created_at)
    )
    return db.scalars(stmt).all()
