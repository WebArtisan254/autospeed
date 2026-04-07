from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .models import db, Entry, User
from sqlalchemy.exc import IntegrityError

def create_entry(*, user_id: int, title: str, attachment_filename: str | None) -> Entry:
    entry = Entry(user_id=user_id, title=title, attachment_filename=attachment_filename)

    db.session.add(entry)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Could not save entry due to a data constraint.")
    except Exception:
        db.session.rollback()
        raise

    return entry

def get_entry(entry_id: int) -> Entry | None:
    return db.session.get(Entry, entry_id)

def list_entries(*, q: str="", page: int=1, per_page: int=10) -> tuple[list[Entry], int]:
    stmt = select(Entry).order_by(Entry.created_at.desc())

    if q:
        stmt = stmt.where(Entry.title.ilike(f"%{q}%"))

    total = db.session.scalars(select(db.func.count()).select_from(stmt.subquery()))

    offset = (page - 1) * per_page
    items = db.session.scalars(stmt.limit(per_page).offset(offset)).all()

    return items, int(total or 0)

def list_users_with_entries() -> list[User]:
    stmt = select(User).options(selectinload(User.entries)).order_by(User.created_at.desc())
    return db.session.scalars(stmt).all()