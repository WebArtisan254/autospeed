from typing import Mapping
from ..models import db, User

class UserError(Exception):
    pass

class ValidationError(UserError):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message

class NotFoundError(UserError):
    pass

class ForbiddenError(UserError):
    pass

def register_user(*, data: Mapping[str, str]) -> User:
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm = data.get("confirm") or ""

    if not username:
        raise ValidationError("username", "Username is required.")
    if len(username) > 80:
        raise ValidationError("username", "Username must be 80 characters or fewer.")
    if not email:
        raise ValidationError("email", "Email is required.")
    if not password:
        raise ValidationError("password", "Password is required.")
    if len(password) < 10:
        raise ValidationError("password", "Use at least 10 characters.")
    if password != confirm:
        raise ValidationError("confirm", "Passwords do not match.")

    existing = db.session.scalars(
        db.select(User).where((User.username == username) | (User.email == email))
    ).first()
    if existing:
        if existing.username == username:
            raise ValidationError("username", "Username is already taken.")
        raise ValidationError("email", "Email is already in use.")

    user = User(username=username, email=email)
    user.set_password(password)

    db.session.add(user)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return user

def update_user_profile(*, user_id: int, data: Mapping[str, str]) -> User:
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found.")

    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()

    if not username:
        raise ValidationError("username", "Username is required.")
    if len(username) > 80:
        raise ValidationError("username", "Username must be 80 characters or fewer.")
    if not email:
        raise ValidationError("email", "Email is required.")

    if username != user.username:
        conflict = db.session.scalars(
            db.select(User).where(User.username == username)
        ).first()
        if conflict:
            raise ValidationError("username", "Username is already taken.")

    if email != user.email:
        conflict = db.session.scalars(
            db.select(User).where(User.email == email)
        ).first()
        if conflict:
            raise ValidationError("email", "Email is already in use.")

    user.username = username
    user.email = email

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return user

def admin_update_user(*, user_id: int, data: Mapping[str, str]) -> User:
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found.")

    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    role = (data.get("role") or "").strip().lower()

    if not username:
        raise ValidationError("username", "Username is required.")
    if not email:
        raise ValidationError("email", "Email is required.")
    if role not in {"member", "admin"}:
        raise ValidationError("role", "Role must be 'member' or 'admin'.")

    if username != user.username:
        conflict = db.session.scalars(
            db.select(User).where(User.username == username)
        ).first()
        if conflict:
            raise ValidationError("username", "Username is already taken.")

    if email != user.email:
        conflict = db.session.scalars(
            db.select(User).where(User.email == email)
        ).first()
        if conflict:
            raise ValidationError("email", "Email is already in use.")

    user.username = username
    user.email = email
    user.role = role

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return user

def delete_user(*, user_id: int) -> None:
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found.")

    db.session.delete(user)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
