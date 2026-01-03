from flask import render_template, g
from app.admin import admin_bp
from app.admin.decorators import admin_required

@admin_bp.route("/")
@admin_required
def dashboard():
    return render_template("admin/dashboard.html")