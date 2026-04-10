from __future__ import annotations
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from .models import db, Entry, User
from sqlalchemy.exc import IntegrityError

def create_user(*, username: str, password: str) -> User:
    user = User(username=username)
    user.set_password(password)

    db.session.add(user)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    
    return user 

def get_user_with_entries(user_id: int) -> User | None:
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.entries))
    )
    return db.session.scalars(stmt).first()

def create_entry(*, user_id: int, title: str, attachment_filename: str | None,
                 attachment_original_name: str | None) -> Entry:
    entry = Entry(user_id=user_id,
                   title=title,
                    attachment_filename=attachment_filename, 
                    attachment_original_name=attachment_original_name)

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

def list_entries(*, user_id: int, q: str="", page: int=1, per_page: int=10) -> tuple[list[Entry], int]:
    stmt = (
        select(Entry)
        .where(Entry.user_id == user_id)
        .order_by(Entry.created_at.desc())
    )

    if q:
        stmt = stmt.where(Entry.title.ilike(f"%{q}%"))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.session.scalar(count_stmt) or 0

    #Applying paging at database level
    offset = (page - 1) * per_page
    items = db.session.scalars(stmt.limit(per_page).offset(offset)).all()

    return items, int(total)

def list_users_with_entries() -> list[User]:
    stmt = select(User).options(selectinload(User.entries)).order_by(User.created_at.desc())
    return db.session.scalars(stmt).all()