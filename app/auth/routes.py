from flask import Blueprint, redirect, url_for, session
from app.services.oauth import oauth
from app.services.firestore import get_db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
def login():
    redirect_uri = url_for("auth.callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route("/callback")
def callback():
    token = oauth.google.authorize_access_token()
    user_info = token["userinfo"]

    db = get_db()

    user_ref = db.collection("users").document(user_info["sub"])
    user_ref.set({
        "email": user_info["email"],
        "name": user_info["name"],
        "picture": user_info["picture"],
        "provider": "google"
    }, merge=True)

    session["user"] = {
        "id": user_info["sub"],
        "email": user_info["email"],
        "name": user_info["name"]
    }

    return redirect("/admin/")