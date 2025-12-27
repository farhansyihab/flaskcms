from flask import Blueprint, render_template, abort
from flask import send_from_directory, current_app
import os

from app.services.firestore import (
    get_published_articles,
    get_article_by_slug,
    get_home_page,
    get_page_by_slug,
    get_all_published_pages
)

public_bp = Blueprint("public", __name__)

@public_bp.route("/")
def home():
    """Halaman beranda - khusus handle slug '/'"""
    home_page = get_home_page()
    
    if home_page:
        return render_template(
            "public/home.html",  # ← Harus ada di app/templates/public/
            page=home_page,
            seo=home_page.get("seo", {}),
            is_home=True
        )
    
    # Fallback jika tidak ada homepage
    return render_template(
        "public/index.html",  # ← Juga di app/templates/public/
        seo={
            "title": "ABI Sumatera Selatan",
            "description": "Website resmi ABI Sumatera Selatan",
        }
    )

@public_bp.route("/<path:slug>")
def page_detail(slug):
    """Halaman statis biasa"""
    # Skip slug tertentu
    if slug in ['', '/']:
        return home()
    
    page = get_page_by_slug(slug)
    if not page:
        abort(404)
    
    return render_template(
        "public/page.html",  # ← Buat file ini nanti
        page=page,
        seo=page.get("seo", {}),
        is_home=False
    )

@public_bp.route("/info/<slug>")
def article_detail(slug):
    """Halaman artikel/berita"""
    article = get_article_by_slug(slug)
    if not article:
        abort(404)

    return render_template(
        "public/info/article.html",  # ← Akan dibuat nanti
        article=article,
        seo={
            "title": article.get("meta_title", article.get("title", "")),
            "description": article.get("meta_description", article.get("excerpt", "")),
            "image": article.get("meta_image"),
        },
    )

@public_bp.route('/includes/<path:filename>')
def includes_files(filename):
    """Serve include files (header, footer, etc.)"""
    # Path ke folder includes
    includes_dir = os.path.join(current_app.root_path, 'templates', 'public', 'includes')
    return send_from_directory(includes_dir, filename)