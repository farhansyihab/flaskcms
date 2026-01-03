from flask import (
    render_template, request, redirect,
    url_for, flash
)
from datetime import datetime

from app.admin import admin_bp
from app.admin.decorators import admin_required
from app.services.firestore import (
    get_pages,
    create_page,
    update_page,
    delete_page,
    get_page_by_id,
)

@admin_bp.route("/pages")
@admin_required
def pages_index():
    pages = []

    for doc in get_pages():
        data = doc.to_dict()
        data["id"] = doc.id
        data.setdefault("title", "Untitled")
        data.setdefault("slug", "")
        data.setdefault("published", False)
        data.setdefault("author", "Unknown")
        data["status"] = "published" if data["published"] else "draft"
        data["created_at"] = data.get("created_at", doc.create_time)

        pages.append(data)

    pages.sort(key=lambda x: x["created_at"], reverse=True)
    return render_template("admin/pages/index.html", pages=pages)


@admin_bp.route("/pages/create", methods=["GET", "POST"])
@admin_required
def pages_create():
    if request.method == "POST":
        data = {
            "title": request.form["title"].strip(),
            "slug": request.form["slug"].strip(),
            "content_html": request.form.get("content", ""),
            "published": request.form.get("status") == "published",
            "created_at": datetime.utcnow(),
        }

        if not data["title"] or not data["slug"]:
            flash("Title & Slug wajib diisi", "danger")
            return render_template("admin/pages/create.html")

        create_page(data)
        flash("Page berhasil dibuat", "success")
        return redirect(url_for("admin.pages_index"))

    return render_template("admin/pages/create.html")

@admin_bp.route("/pages/<page_id>/edit", methods=["GET", "POST"])
@admin_required
def pages_edit(page_id):
    doc = get_page_by_id(page_id)
    if not doc or not doc.exists:
        flash("Page not found", "danger")
        return redirect(url_for("admin.pages_index"))

    page = doc.to_dict()
    page["id"] = doc.id

    if request.method == "POST":
        update_data = {
            "title": request.form.get("title", "").strip(),
            "slug": request.form.get("slug", "").strip(),
            "content_html": request.form.get("content", ""),
            "published": request.form.get("status") == "published",
        }

        update_page(page_id, update_data)
        flash("Page updated successfully", "success")
        return redirect(url_for("admin.pages_index"))

    page["status"] = "published" if page.get("published") else "draft"
    return render_template("admin/pages/edit.html", page=page)


@admin_bp.route("/pages/<page_id>/delete", methods=["POST"])
@admin_required
def pages_delete(page_id):
    delete_page(page_id)
    flash("Page deleted successfully", "success")
    return redirect(url_for("admin.pages_index"))
