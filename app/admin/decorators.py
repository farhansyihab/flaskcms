from functools import wraps
from flask import session, redirect, url_for, g, abort
from .permissions import is_admin

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = session.get("user")
        if not user:
            return redirect(url_for("auth.login"))

        g.user = user
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = session.get("user")

        if not user:
            return redirect(url_for("auth.login"))

        if not is_admin(user):
            abort(403)

        # normalize user
        user["is_admin"] = True
        g.user = user

        return f(*args, **kwargs)
    return wrapper