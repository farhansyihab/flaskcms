from flask import Blueprint, render_template, request, redirect, url_for, g, session
from app.admin.decorators import admin_required
from app.services.firestore import get_pages, create_page

admin_bp = Blueprint(
    "admin",
    __name__,
    template_folder="templates"
)

# HAPUS middleware ini karena sudah dihandle di decorator
# @admin_bp.before_request
# def load_user():
#     user_session = session.get("user")
#     if user_session:
#         g.user = user_session
#     else:
#         g.user = None

# =====================
# Dashboard
# =====================
@admin_bp.route("/")
@admin_required
def dashboard():
    print(f"DASHBOARD: g.user = {g.user}")  # Debug
    return render_template("admin/dashboard.html")

# =====================
# Pages Index
# =====================
@admin_bp.route("/pages")
@admin_required
def pages_index():
    try:
        pages = []
        for doc in get_pages():
            page_data = doc.to_dict()
            page_data["id"] = doc.id
            pages.append(page_data)
    except Exception as e:
        print(f"Error getting pages: {e}")
        pages = []  # Return empty list jika error
    
    return render_template("admin/pages/index.html", pages=pages)

# =====================
# Pages Create
# =====================
@admin_bp.route("/pages/create", methods=["GET", "POST"])
@admin_required
def pages_create():
    if request.method == "POST":
        try:
            page_data = {
                "title": request.form.get("title", ""),
                "slug": request.form.get("slug", ""),
                "content": request.form.get("content", ""),
                "status": request.form.get("status", "draft"),
                "author": g.user.get("name", "Unknown") if g.user else "Unknown",
                "seo": {
                    "meta_title": request.form.get("meta_title", ""),
                    "meta_description": request.form.get("meta_description", "")
                }
            }
            create_page(page_data)
            return redirect(url_for("admin.pages_index"))
        except Exception as e:
            print(f"Error creating page: {e}")
            return "Error creating page", 500

    return render_template("admin/pages/create.html")

# =====================
# News Management
# =====================
@admin_bp.route("/news")
@admin_required
def news_index():
    # Sementara return template kosong
    return render_template("admin/news/index.html")

# =====================
# Logout
# =====================
@admin_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("public.home"))