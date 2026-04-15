from flask import Blueprint, current_app, redirect, url_for, session, request, flash
from flask_login import login_user
from datetime import datetime
from sqlalchemy import select
from .models import User_Token, db, User, OAuthIdentity
from .db_access import create_user
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError

bp = Blueprint("oauth", __name__, url_prefix="/auth/oauth")
oauth = OAuth()

def init_oauth(app):
    oauth.init_app(app)

    oauth.register(
        name="google", 
        client_id=app.config["GOOGLE_CLIENT_ID"],
        #client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

@bp.get("/google")
def google_login():
    redirect_uri = url_for("oauth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@bp.get("/google/callback")
def google_callback():
    try: 
        token = oauth.google.authorize_access_token()
    except OAuthError:
        flash("OAuth login failed. Please try again.")
        return redirect(url_for("auth.login"))
    
    userinfo = oauth.google.parse_id_token(token)

    provider = "google"
    provider_user_id = str(userinfo.get("sub") or "")
    email = (userinfo.get("email") or "").strip().lower() or None
    email_verified = bool(userinfo.get("email_verified") is True)

    if not provider_user_id:
        flash("OAuth login failed. Please try again.")
        return redirect(url_for("auth.login"))
    
    identity = db.session.scalars(
        select(OAuthIdentity)
        .where(OAuthIdentity.provider == provider)
        .where(OAuthIdentity.provider_user_id == provider_user_id)
    ).first()

    if identity:
        user = db.session.get(User, identity.user_id)
        if user is None:
            flash("OAuth login failed. Please try again.")
            return redirect(url_for("auth.login"))
        else:
            user = None
            if email:
                user = db.session.scalars(select(User).where(User.email == email)).first()

            if user is None:
                username = (userinfo.get("name") or "user").strip()[:30].replace("","_").lower()
                fallback_username = f"{username}_{provider_user_id[-6:]}"
                user = create_user(username=fallback_username, password=User_Token.generate_token())
                user.email = email or f"{provider_user_id}@{provider}.local"
                user.email_verified = bool(email_verified and email)

                db.session.commit()
            
            identity = OAuthIdentity(
                provider=provider,
                provider_user_id=provider_user_id,
                email=email,
                email_verified=email_verified,
                user_id=user.id
            )
            db.session.add(identity)
            db.session.commit()

        login_user(user)
        session["auth_issued_at"] = datetime.utcnow().timestamp()
        flash("You are now logged in.")
        return redirect(url_for("entries.index"))