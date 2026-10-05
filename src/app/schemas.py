import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .models import WorkItemStatus


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    email: EmailStr
    hashed_password: str = Field(min_length=1)


class UserRead(ORMModel):
    user_id: uuid.UUID
    username: str
    email: str
    created_at: datetime


class ProjectCreate(BaseModel):
    owner_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ProjectRead(ORMModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    title: str
    description: str | None
    is_deleted: bool
    created_at: datetime


class WorkItemCreate(BaseModel):
    project_id: uuid.UUID
    creator_id: uuid.UUID
    human_id: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: WorkItemStatus = WorkItemStatus.todo
    extrafields: dict[str, Any] = Field(default_factory=dict)


class WorkItemRead(ORMModel):
    id: uuid.UUID
    project_id: uuid.UUID
    creator_id: uuid.UUID
    human_id: str
    title: str
    description: str | None
    status: WorkItemStatus
    extrafields: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class WorkItemStatusUpdate(BaseModel):
    status: WorkItemStatus


class CommentCreate(BaseModel):
    author_id: uuid.UUID
    message: str = Field(min_length=1)


class CommentRead(ORMModel):
    id: uuid.UUID
    work_item_id: uuid.UUID
    author_id: uuid.UUID
    message: str
    created_at: datetime


class EstimationUpsert(BaseModel):
    storypoints: int | None = Field(default=None, ge=0)
    hours_estim: int | None = Field(default=None, ge=0)
    hours_spent: int | None = Field(default=None, ge=0)
    hours_remain: int | None = Field(default=None, ge=0)


class EstimationRead(ORMModel):
    work_item_id: uuid.UUID
    storypoints: int | None
    hours_estim: int | None
    hours_spent: int | None
    hours_remain: int | None
