from __future__ import annotations
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Table, Column
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

entry_tags = Table(
    "entry_tags",
    db.metadata,
    Column("entry_id", ForeignKey("entries.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

class Tag(db.Model):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    entries: Mapped[list["Entry"]] = relationship(
        secondary=entry_tags,
        back_populates="tags",
    )
class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    entries: Mapped[List["Entry"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan", 
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class Entry(db.Model):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="entries")

    attachment_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    attachment_original_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")

    attachments: Mapped[List["Attachment"]] = relationship(
        back_populates="entry",
        cascade="all, delete-orphan",
    )

    tags: Mapped[list["Tag"]] = relationship(
        secondary=entry_tags, 
        back_populates="entries",
    )

class Attachment(db.Model):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stored_name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    entry_id: Mapped[int] = mapped_column(ForeignKey("entries.id"), nullable=False)
    entry: Mapped["Entry"] = relationship(back_populates="attachments")