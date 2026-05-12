from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Note, Tag, User
from app.schemas import NoteCreate, NoteRead, NoteUpdate


router = APIRouter(prefix="/notes", tags=["notes"])


def _normalize_tag_names(names: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for raw in names:
        cleaned = raw.strip().lower()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result


def _get_or_create_tags(db: Session, user_id: int, names: list[str]) -> list[Tag]:
    normalized = _normalize_tag_names(names)
    if not normalized:
        return []

    existing = (
        db.query(Tag)
        .filter(Tag.user_id == user_id, Tag.name.in_(normalized))
        .all()
    )
    existing_names = {t.name for t in existing}

    new_tags = [
        Tag(user_id=user_id, name=name)
        for name in normalized
        if name not in existing_names
    ]
    for tag in new_tags:
        db.add(tag)
    if new_tags:
        db.flush()

    return existing + new_tags


def _get_owned_note(db: Session, note_id: int, user_id: int) -> Note:
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == user_id)
        .first()
    )
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    return note


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(
    note_in: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Note:
    note = Note(
        user_id=current_user.id,
        title=note_in.title,
        content=note_in.content,
        tags=_get_or_create_tags(db, current_user.id, note_in.tag_names),
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("", response_model=list[NoteRead])
def list_notes(
    q: str | None = Query(default=None, description="Search title and content"),
    tag: str | None = Query(default=None, description="Filter by tag name"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Note]:
    query = db.query(Note).filter(Note.user_id == current_user.id)

    if q:
        like = f"%{q}%"
        query = query.filter(or_(Note.title.ilike(like), Note.content.ilike(like)))

    if tag:
        normalized_tag = tag.strip().lower()
        query = query.join(Note.tags).filter(Tag.name == normalized_tag)

    return (
        query.order_by(Note.updated_at.desc()).offset(skip).limit(limit).all()
    )


@router.get("/{note_id}", response_model=NoteRead)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Note:
    return _get_owned_note(db, note_id, current_user.id)


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(
    note_id: int,
    note_in: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Note:
    note = _get_owned_note(db, note_id, current_user.id)
    data = note_in.model_dump(exclude_unset=True)

    if "tag_names" in data:
        tag_names = data.pop("tag_names") or []
        note.tags = _get_or_create_tags(db, current_user.id, tag_names)

    for field, value in data.items():
        setattr(note, field, value)

    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    note = _get_owned_note(db, note_id, current_user.id)
    db.delete(note)
    db.commit()
