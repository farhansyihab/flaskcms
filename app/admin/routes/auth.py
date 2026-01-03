from flask import redirect, url_for, session, flash
from app.admin import admin_bp

@admin_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("public.home"))