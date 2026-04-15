from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=list[str])
def list_tags(db: Session = Depends(get_db)):
    """Return all distinct tags used across books."""
    rows = db.query(func.unnest(Book.tags).label("tag")).distinct().order_by("tag").all()
    return [row.tag for row in rows]
