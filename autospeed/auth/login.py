from flask_login import LoginManager
from ..models import db, User

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id: str):
    try:
        uid = int(user_id)
    except ValueError:
        return None
    return db.session.get(User,uid)