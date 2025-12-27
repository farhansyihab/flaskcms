from flask import Blueprint, render_template, abort
from app.services.firestore import (
    get_published_articles,
    get_article_by_slug,
    get_page_by_slug,
    get_home_page  # Kita akan buat fungsi ini
)

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    """Halaman beranda - cek apakah ada page dengan slug 'home' atau 'beranda'"""
    # Coba cari halaman beranda
    home_page = None
    
    # Coba slug 'home' dulu
    home_page = get_page_by_slug("home")
    
    # Jika tidak ada, coba 'beranda'
    if not home_page:
        home_page = get_page_by_slug("beranda")
    
    # Jika ada halaman beranda, tampilkan
    if home_page:
        return render_template(
            "public/page.html",  # Template untuk halaman biasa
            page=home_page,
            seo={
                "title": home_page.get("seo", {}).get("meta_title", home_page["title"]),
                "description": home_page.get("seo", {}).get("meta_description", ""),
            },
            is_home=True  # Flag khusus untuk template
        )
    
    # Jika tidak ada halaman beranda, tampilkan default
    try:
        articles = [doc.to_dict() for doc in get_published_articles()]
    except:
        articles = []
    
    return render_template(
        "public/index.html",  # Template default
        articles=articles,
        seo={
            "title": "ABI Sumatera Selatan",
            "description": "Website resmi ABI Sumatera Selatan",
        },
        is_home=True
    )


@public_bp.route("/<slug>")
def page_detail(slug):
    """Halaman statis biasa"""
    # Skip slug tertentu yang sudah ditangani
    if slug in ['home', 'beranda']:
        return home()
    
    page = get_page_by_slug(slug)
    if not page:
        abort(404)
    
    return render_template(
        "public/page.html",
        page=page,
        seo={
            "title": page.get("seo", {}).get("meta_title", page["title"]),
            "description": page.get("seo", {}).get("meta_description", ""),
        },
        is_home=False
    )


@public_bp.route("/info/<slug>")
def article_detail(slug):
    """Halaman artikel/berita"""
    article = get_article_by_slug(slug)
    if not article:
        abort(404)

    return render_template(
        "public/info/article.html",
        article=article,
        seo={
            "title": article.get("meta_title", article["title"]),
            "description": article.get("meta_description", article.get("excerpt", "")),
            "image": article.get("meta_image"),
        },
    )