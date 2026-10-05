import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class WorkItemStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    owned_projects: Mapped[list["Project"]] = relationship(back_populates="owner")
    memberships: Mapped[list["ProjectMember"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    created_work_items: Mapped[list["WorkItem"]] = relationship(back_populates="creator")
    comments: Mapped[list["Comment"]] = relationship(back_populates="author")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    owner: Mapped[User] = relationship(back_populates="owned_projects")
    members: Mapped[list["ProjectMember"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    work_items: Mapped[list["WorkItem"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class ProjectMember(Base):
    __tablename__ = "project_members"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, index=True)

    project: Mapped[Project] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="memberships")


class WorkItem(Base):
    __tablename__ = "work_items"
    __table_args__ = (
        UniqueConstraint("project_id", "human_id", name="uq_work_items_project_human_id"),
        Index("idx_work_items_project_status", "project_id", "status"),
        Index("idx_work_items_creator", "creator_id"),
        Index("idx_work_items_project_created_at", "project_id", "created_at"),
        Index("idx_work_items_extrafields_gin", "extrafields", postgresql_using="gin"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    creator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    human_id: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[WorkItemStatus] = mapped_column(
        Enum(WorkItemStatus, name="work_item_status"),
        nullable=False,
        default=WorkItemStatus.todo,
        server_default=WorkItemStatus.todo.value,
    )
    extrafields: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    project: Mapped[Project] = relationship(back_populates="work_items")
    creator: Mapped[User] = relationship(back_populates="created_work_items")
    estimation: Mapped["WorkItemEstim | None"] = relationship(back_populates="work_item", uselist=False, cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship(back_populates="work_item", cascade="all, delete-orphan")


class WorkItemEstim(Base):
    __tablename__ = "work_item_estim"
    __table_args__ = (
        CheckConstraint("storypoints IS NULL OR storypoints >= 0"),
        CheckConstraint("hours_estim IS NULL OR hours_estim >= 0"),
        CheckConstraint("hours_spent IS NULL OR hours_spent >= 0"),
        CheckConstraint("hours_remain IS NULL OR hours_remain >= 0"),
    )

    work_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("work_items.id", ondelete="CASCADE"), primary_key=True)
    storypoints: Mapped[int | None] = mapped_column(Integer)
    hours_estim: Mapped[int | None] = mapped_column(Integer)
    hours_spent: Mapped[int | None] = mapped_column(Integer)
    hours_remain: Mapped[int | None] = mapped_column(Integer)

    work_item: Mapped[WorkItem] = relationship(back_populates="estimation")


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (
        Index("idx_comments_work_item_created_at", "work_item_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    work_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("work_items.id", ondelete="CASCADE"), nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    work_item: Mapped[WorkItem] = relationship(back_populates="comments")
    author: Mapped[User] = relationship(back_populates="comments")
