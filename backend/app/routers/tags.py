from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Tag, User
from app.schemas import TagRead


router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
def list_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Tag]:
    return (
        db.query(Tag)
        .filter(Tag.user_id == current_user.id)
        .order_by(Tag.name)
        .all()
    )
