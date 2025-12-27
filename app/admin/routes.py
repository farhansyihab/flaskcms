from flask import Blueprint, render_template, request, redirect, url_for, g, session, flash, jsonify
from app.admin.decorators import admin_required
# from app.services.firestore import get_pages, create_page, update_page, delete_page, get_page_by_id
from app.services.firestore import (
    get_pages, 
    create_page, 
    update_page, 
    delete_page, 
    get_page_by_id
)
from datetime import datetime
import traceback

admin_bp = Blueprint(
    "admin",
    __name__,
    template_folder="templates"
)

@admin_bp.route("/")
@admin_required
def dashboard():
    print(f"DASHBOARD: g.user = {g.user}")
    return render_template("admin/dashboard.html")

@admin_bp.route("/pages")
@admin_required
def pages_index():
    try:
        print("📂 Loading pages from Firestore...")
        
        pages = []
        for doc in get_pages():
            page_data = doc.to_dict()
            page_data["id"] = doc.id
            
            # 🔧 Format data untuk template
            # 1. Pastikan field required ada
            if "title" not in page_data:
                page_data["title"] = "Untitled"
            
            if "slug" not in page_data:
                page_data["slug"] = ""
            
            if "published" not in page_data:
                page_data["published"] = False
            
            # 2. Tambahkan status untuk template
            page_data["status"] = "published" if page_data.get("published") else "draft"
            
            # 3. Tambahkan timestamp jika ada
            if "created_at" not in page_data:
                if hasattr(doc, 'create_time'):
                    page_data["created_at"] = doc.create_time
                else:
                    page_data["created_at"] = datetime.utcnow()
            
            # 4. Pastikan author ada
            if "author" not in page_data:
                page_data["author"] = "Unknown"
            
            pages.append(page_data)
            print(f"   ✅ Loaded: {page_data['title']} (ID: {doc.id})")
        
        # Sort secara manual di Python (karena tidak bisa order_by di Firestore tanpa index)
        pages.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        
        print(f"\n📊 Total pages loaded: {len(pages)}")
        
    except Exception as e:
        print(f"❌ Error in pages_index: {e}")
        traceback.print_exc()
        pages = []
        flash("Error loading pages", "danger")
    
    return render_template("admin/pages/index.html", pages=pages)

@admin_bp.route("/pages/create", methods=["GET", "POST"])
@admin_required
def pages_create():
    if request.method == "POST":
        try:
            print("📝 Creating new page...")
            
            page_data = {
                "title": request.form.get("title", "").strip(),
                "slug": request.form.get("slug", "").strip(),
                "content_html": request.form.get("content", ""),
                "published": request.form.get("status") == "published",
                "author": g.user.get("name", "Unknown") if g.user else "Unknown",
                "created_at": datetime.utcnow(),
                "seo": {
                    "title": request.form.get("meta_title", "").strip() or request.form.get("title", "").strip(),
                    "description": request.form.get("meta_description", "").strip(),
                    "image": ""
                }
            }
            
            # Validasi
            if not page_data["title"]:
                flash("Title is required", "danger")
                return render_template("admin/pages/create.html")
            
            if not page_data["slug"]:
                flash("Slug is required", "danger")
                return render_template("admin/pages/create.html")
            
            create_page(page_data)
            flash("Page created successfully!", "success")
            print("✅ Page created successfully!")
            
            return redirect(url_for("admin.pages_index"))
            
        except Exception as e:
            print(f"❌ Error creating page: {e}")
            traceback.print_exc()
            flash(f"Error creating page: {str(e)}", "danger")
            return render_template("admin/pages/create.html")
    
    return render_template("admin/pages/create.html")

@admin_bp.route("/pages/<page_id>/edit", methods=["GET", "POST"])
@admin_required
def pages_edit(page_id):
    try:
        # Get page data
        doc = get_page_by_id(page_id)
        if not doc or not doc.exists:
            flash("Page not found", "danger")
            return redirect(url_for("admin.pages_index"))
        
        page_data = doc.to_dict()
        page_data["id"] = doc.id
        
        if request.method == "POST":
            # Update page
            update_data = {
                "title": request.form.get("title", "").strip(),
                "slug": request.form.get("slug", "").strip(),
                "content_html": request.form.get("content", ""),
                "published": request.form.get("status") == "published",
                "updated_at": datetime.utcnow(),
                "seo.title": request.form.get("meta_title", "").strip() or request.form.get("title", "").strip(),
                "seo.description": request.form.get("meta_description", "").strip(),
            }
            
            update_page(page_id, update_data)
            flash("Page updated successfully!", "success")
            return redirect(url_for("admin.pages_index"))
        
        # Convert boolean published to string status for form
        page_data["status"] = "published" if page_data.get("published") else "draft"
        
        return render_template("admin/pages/edit.html", page=page_data)
        
    except Exception as e:
        print(f"❌ Error editing page: {e}")
        traceback.print_exc()
        flash(f"Error editing page: {str(e)}", "danger")
        return redirect(url_for("admin.pages_index"))

@admin_bp.route("/pages/<page_id>/delete", methods=["POST"])
@admin_required
def pages_delete(page_id):
    try:
        delete_page(page_id)
        flash("Page deleted successfully!", "success")
        print(f"✅ Page {page_id} deleted")
    except Exception as e:
        print(f"❌ Error deleting page: {e}")
        flash(f"Error deleting page: {str(e)}", "danger")
    
    return redirect(url_for("admin.pages_index"))

@admin_bp.route("/news")
@admin_required
def news_index():
    return render_template("admin/news/index.html")

@admin_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("public.home"))

# Debug endpoint
@admin_bp.route("/health")
def health_check():
    return jsonify({
        "status": "healthy",
        "user": g.user.get("email") if hasattr(g, 'user') else None,
        "timestamp": datetime.utcnow().isoformat()
    })