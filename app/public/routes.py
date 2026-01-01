from flask import Blueprint, current_app, render_template, abort, request, send_from_directory
import os

from app.services.firestore import (
    get_published_articles,  # ← fungsi baru sudah return list of dict
    get_article_by_slug,
    get_home_page,
    get_page_by_slug,
    get_all_published_pages
)

public_bp = Blueprint("public", __name__)

# Default values untuk SEO
DEFAULT_TITLE = "DPW ABI Sumatera Selatan"
DEFAULT_DESCRIPTION = "Website resmi DPW ABI Sumatera Selatan"
DEFAULT_IMAGE = "https://farhansyihab.github.io/abi-firebase/public/img/icons/apple-touch-icon-180x180.png"
SITE_URL = "https://abisumsel.org"

@public_bp.route("/")
def home():
    """Halaman beranda"""
    home_page = get_home_page()
    
    if home_page:
        return render_template(
            "public/home.html",
            page=home_page,
            is_home=True
        )
    
    # Fallback jika tidak ada homepage
    return render_template(
        "public/index.html",
        page={
            "title": DEFAULT_TITLE,
            "seo": {
                "title": DEFAULT_TITLE,
                "description": DEFAULT_DESCRIPTION,
                "image": DEFAULT_IMAGE,
                "og_title": DEFAULT_TITLE,
                "og_description": DEFAULT_DESCRIPTION,
                "og_image": DEFAULT_IMAGE,
                "twitter_card": "summary_large_image",
                "twitter_title": DEFAULT_TITLE,
                "twitter_description": DEFAULT_DESCRIPTION,
                "twitter_image": DEFAULT_IMAGE
            }
        },
        is_home=True
    )

@public_bp.route("/<path:slug>/")
def page_detail(slug):
    """Halaman statis biasa"""
    # Skip slug tertentu
    if slug in ['', '/']:
        return home()
    
    page = get_page_by_slug(slug)
    if not page:
        abort(404)
    
    # Tambahkan URL lengkap untuk schema.org
    if "schema" in page and isinstance(page["schema"], dict):
        page["schema"]["url"] = f"{SITE_URL}/{slug}"
    
    return render_template(
        "public/page.html",
        page=page,
        is_home=False
    )

@public_bp.route("/info/<slug>/")
def article_detail(slug):
    """Halaman artikel/berita"""
    article = get_article_by_slug(slug)
    if not article:
        abort(404)

    # Siapkan SEO data untuk artikel
    seo_data = {
        "title": article.get("meta_title", article.get("title", DEFAULT_TITLE)),
        "description": article.get("meta_description", article.get("excerpt", DEFAULT_DESCRIPTION)),
        "image": article.get("meta_image", DEFAULT_IMAGE),
        "og_title": article.get("meta_title", article.get("title", DEFAULT_TITLE)),
        "og_description": article.get("meta_description", article.get("excerpt", DEFAULT_DESCRIPTION)),
        "og_image": article.get("meta_image", DEFAULT_IMAGE),
        "twitter_card": "summary_large_image",
        "twitter_title": article.get("meta_title", article.get("title", DEFAULT_TITLE)),
        "twitter_description": article.get("meta_description", article.get("excerpt", DEFAULT_DESCRIPTION)),
        "twitter_image": article.get("meta_image", DEFAULT_IMAGE)
    }
    
    article["seo"] = seo_data

    return render_template(
        "public/info/article.html",
        article=article
    )

@public_bp.route("/info/")
def article_list():
    """Halaman daftar artikel"""
    try:
        articles = get_published_articles(limit=20)  # ← sudah list of dict
        
        return render_template(
            "public/info/index.html",
            articles=articles,
            page={  # Untuk SEO
                "title": "Info & Berita - DPW ABI Sumatera Selatan",
                "seo": {
                    "title": "Info & Berita - DPW ABI Sumatera Selatan",
                    "description": "Kumpulan berita dan informasi terkini dari DPW ABI Sumatera Selatan",
                    "image": DEFAULT_IMAGE,
                    "og_title": "Info & Berita - DPW ABI Sumatera Selatan",
                    "og_description": "Kumpulan berita dan informasi terkini dari DPW ABI Sumatera Selatan",
                    "og_image": DEFAULT_IMAGE,
                    "twitter_card": "summary_large_image",
                    "twitter_title": "Info & Berita - DPW ABI Sumatera Selatan",
                    "twitter_description": "Kumpulan berita dan informasi terkini dari DPW ABI Sumatera Selatan",
                    "twitter_image": DEFAULT_IMAGE
                }
            }
        )
    except Exception as e:
        print(f"❌ Error loading articles: {e}")
        import traceback
        traceback.print_exc()
        return render_template(
            "public/info/index.html",
            articles=[],
            page={
                "title": "Info & Berita",
                "seo": {
                    "title": "Info & Berita - DPW ABI Sumatera Selatan",
                    "description": "Kumpulan berita dan informasi terkini",
                    "image": DEFAULT_IMAGE,
                    "og_title": "Info & Berita - DPW ABI Sumatera Selatan",
                    "og_description": "Kumpulan berita dan informasi terkini",
                    "og_image": DEFAULT_IMAGE,
                    "twitter_card": "summary_large_image",
                    "twitter_title": "Info & Berita - DPW ABI Sumatera Selatan",
                    "twitter_description": "Kumpulan berita dan informasi terkini",
                    "twitter_image": DEFAULT_IMAGE
                }
            }
        )

@public_bp.route('/includes/<path:filename>')
def includes_files(filename):
    """Serve include files (header, footer, etc.)"""
    try:
        # Path ke folder includes
        includes_dir = os.path.join(
            current_app.root_path, 
            'templates', 
            'public', 
            'includes'
        )
        
        # Debug info
        print(f"🔍 Serving include file: {filename}")
        print(f"   Directory: {includes_dir}")
        print(f"   Full path: {os.path.join(includes_dir, filename)}")
        
        # Cek apakah file ada
        if not os.path.exists(os.path.join(includes_dir, filename)):
            print(f"❌ File not found: {filename}")
            abort(404)
        
        return send_from_directory(includes_dir, filename)
        
    except Exception as e:
        print(f"❌ Error serving include file {filename}: {e}")
        abort(404)

@public_bp.route("/search/")
def search_page():
    """Halaman pencarian client-side"""
    return render_template(
        "public/search.html",
        page={
            "title": "Pencarian - DPW ABI Sumatera Selatan",
            "seo": {
                "title": "Pencarian - DPW ABI Sumatera Selatan",
                "description": "Cari artikel dan halaman di website DPW ABI Sumatera Selatan",
                "image": DEFAULT_IMAGE,
                "og_title": "Pencarian - DPW ABI Sumatera Selatan",
                "og_description": "Cari artikel dan halaman di website DPW ABI Sumatera Selatan",
                "og_image": DEFAULT_IMAGE,
                "twitter_card": "summary_large_image",
                "twitter_title": "Pencarian - DPW ABI Sumatera Selatan",
                "twitter_description": "Cari artikel dan halaman di website DPW ABI Sumatera Selatan",
                "twitter_image": DEFAULT_IMAGE
            }
        }
    )        