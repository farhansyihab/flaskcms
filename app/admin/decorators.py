from functools import wraps
from flask import redirect, url_for, g, abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(g, "user", None):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(g, "user", None):
            return redirect(url_for("auth.login"))

        if not g.user.get("is_admin", False):
            abort(403)

        return f(*args, **kwargs)
    return decorated_function
