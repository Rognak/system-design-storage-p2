from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(**payload.model_dump())
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="username or email already exists")
    db.refresh(user)
    return user


@router.get("", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.created_at)).all()
