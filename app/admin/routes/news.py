from flask import render_template, request, redirect, url_for, flash
from datetime import datetime
import traceback

from app.admin import admin_bp
from app.admin.decorators import admin_required
from app.services.firestore import (
    get_published_articles,
    create_article,
    update_article,
    delete_article,
    get_article_by_id,
)

@admin_bp.route("/news")
@admin_required
def news_index():
    articles = get_published_articles(limit=50)
    return render_template("admin/news/index.html", articles=articles)


@admin_bp.route("/news/create", methods=["GET", "POST"])
@admin_required
def news_create():
    if request.method == "POST":
        data = {
            "title": request.form["title"].strip(),
            "slug": request.form["slug"].strip(),
            "content": request.form.get("content", ""),
            "published": request.form.get("status") == "published",
            "created_at": datetime.utcnow(),
        }

        if not data["title"] or not data["slug"]:
            flash("Title & Slug wajib diisi", "danger")
            return render_template("admin/news/create.html")

        create_article(data)
        flash("Artikel berhasil dibuat", "success")
        return redirect(url_for("admin.news_index"))

    return render_template("admin/news/create.html")

@admin_bp.route("/news/<article_id>/edit", methods=["GET", "POST"])
@admin_required
def news_edit(article_id):
    try:
        # Get article data
        doc = get_article_by_id(article_id)
        if not doc or not doc.exists:
            flash("Article not found", "danger")
            return redirect(url_for("admin.news_index"))
        
        article_data = doc.to_dict()
        article_data["id"] = doc.id
        
        if request.method == "POST":
            # Update article
            update_data = {
                "title": request.form.get("title", "").strip(),
                "slug": request.form.get("slug", "").strip(),
                "content": request.form.get("content", ""),
                "excerpt": request.form.get("excerpt", "").strip(),
                "published": request.form.get("status") == "published",
                "meta_title": request.form.get("meta_title", "").strip(),
                "meta_description": request.form.get("meta_description", "").strip(),
                "meta_image": request.form.get("meta_image", "").strip(),
                "updated_at": datetime.utcnow()
            }
            
            # Jika author belum ada, tambahkan
            if "author" not in article_data or not article_data["author"]:
                update_data["author"] = g.user.get("name", "Unknown") if g.user else "Unknown"
            
            update_article(article_id, update_data)
            flash("Article updated successfully!", "success")
            return redirect(url_for("admin.news_index"))
        
        # Convert boolean published to string status for form
        article_data["status"] = "published" if article_data.get("published", False) else "draft"
        
        # Pastikan field ada
        if "meta_title" not in article_data:
            article_data["meta_title"] = article_data.get("title", "")
        if "meta_description" not in article_data:
            article_data["meta_description"] = article_data.get("excerpt", "")
        if "meta_image" not in article_data:
            article_data["meta_image"] = ""
        
        return render_template("admin/news/edit.html", article=article_data)
        
    except Exception as e:
        print(f"❌ Error editing article: {e}")
        traceback.print_exc()
        flash(f"Error editing article: {str(e)}", "danger")
        return redirect(url_for("admin.news_index"))

@admin_bp.route("/news/<article_id>/delete", methods=["POST"])
@admin_required
def news_delete(article_id):
    try:
        delete_article(article_id)
        flash("Article deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting article: {str(e)}", "danger")
    return redirect(url_for("admin.news_index"))