from flask import Blueprint, redirect, url_for, session
from app.services.oauth import oauth
from app.services.firestore import get_db
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
def login():
    redirect_uri = url_for("auth.callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route("/callback")
def callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info = token["userinfo"]
        
        print(f"\n=== AUTH CALLBACK ===")
        print(f"Email: {user_info['email']}")
        print(f"Name: {user_info['name']}")

        # =========================================
        # SIMPLE FIX: Hardcode admin untuk testing
        # =========================================
        # List email yang dianggap admin
        ADMIN_EMAILS = [
            "agiptek@gmail.com",
            "farhanchehaab@gmail.com",
            "admin@abisumsel.org"
        ]
        
        is_admin = user_info["email"] in ADMIN_EMAILS
        print(f"Admin check: {is_admin} (email in admin list)")
        
        # =========================================
        # SET SESSION - PASTIKAN is_admin ADA
        # =========================================
        session["user"] = {
            "id": user_info["sub"],
            "email": user_info["email"],
            "name": user_info["name"],
            "picture": user_info.get("picture", ""),
            "is_admin": is_admin,  # ← HARUS ADA
            "role": "admin" if is_admin else "user"  # ← juga tambahkan role
        }
        
        print(f"✅ Session saved:")
        print(f"   - is_admin: {session['user']['is_admin']}")
        print(f"   - role: {session['user']['role']}")
        
        # =========================================
        # SIMPAN KE FIRESTORE (optional)
        # =========================================
        try:
            db = get_db()
            user_ref = db.collection("users").document(user_info["sub"])
            user_ref.set({
                "email": user_info["email"],
                "name": user_info["name"],
                "picture": user_info.get("picture", ""),
                "provider": "google",
                "is_admin": is_admin,
                "role": "admin" if is_admin else "user",
                "last_login": datetime.utcnow()
            }, merge=True)
            print("✅ User saved to Firestore")
        except Exception as e:
            print(f"⚠️ Firestore error (ignored for now): {e}")
        
        return redirect("/admin/")
        
    except Exception as e:
        print(f"❌ Auth error: {e}")
        import traceback
        traceback.print_exc()
        return "Authentication failed", 500
