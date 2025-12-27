from functools import wraps
from flask import redirect, url_for, g, abort, session

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("auth.login"))
        g.user = session.get("user")
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("=== ENHANCED ADMIN_REQUIRED DEBUG ===")
        
        # 1. Cek session ada user
        if "user" not in session:
            print("❌ No user in session")
            return redirect(url_for("auth.login"))
        
        user_data = session.get("user")
        print(f"User data from session: {user_data}")
        
        # 2. Multiple ways to check admin status
        is_admin = False
        
        # Check 1: Direct is_admin field
        if user_data.get("is_admin") == True:
            is_admin = True
            print("✓ Admin via is_admin field")
        
        # Check 2: role field
        elif user_data.get("role") == "admin":
            is_admin = True
            print("✓ Admin via role field")
        
        # Check 3: email-based admin (for testing)
        elif user_data.get("email") in ["agiptek@gmail.com", "admin@example.com"]:
            is_admin = True
            print("✓ Admin via email check")
        
        # Check 4: Update session if missing is_admin
        if not is_admin:
            print("❌ User is NOT admin")
            abort(403)
        
        # 3. Ensure is_admin is in user_data for templates
        user_data["is_admin"] = True
        g.user = user_data
        
        print(f"✅ User is ADMIN: {user_data['email']}")
        return f(*args, **kwargs)
    return decorated_function