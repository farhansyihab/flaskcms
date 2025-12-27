from flask import Blueprint, render_template, request, redirect, url_for, g
from app.admin.decorators import admin_required
from app.services.firestore import get_pages, create_page

admin_bp = Blueprint(
    "admin",
    __name__,
    template_folder="templates"
)

# =====================
# Pages Index
# =====================
@admin_bp.route("/pages")
@admin_required
def pages_index():
    pages = [
        {"id": doc.id, **doc.to_dict()}
        for doc in get_pages()
    ]
    return render_template("admin/pages/index.html", pages=pages)


# =====================
# Pages Create
# =====================
@admin_bp.route("/pages/create", methods=["GET", "POST"])
@admin_required
def pages_create():
    if request.method == "POST":
        create_page({
            "title": request.form["title"],
            "slug": request.form["slug"],
            "content": request.form["content"],
            "status": request.form["status"],
            "author": g.user,  # ⬅️ FIX: jangan pakai request.user
            "seo": {
                "meta_title": request.form.get("meta_title"),
                "meta_description": request.form.get("meta_description")
            }
        })
        return redirect(url_for("admin.pages_index"))

    return render_template("admin/pages/create.html")