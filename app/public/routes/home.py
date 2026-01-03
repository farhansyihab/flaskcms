from flask import render_template, abort

from app.services.firestore import (
    get_home_page,
    get_page_by_slug,
)
from app.public import public_bp
# Default values untuk SEO
DEFAULT_TITLE = "DPW ABI Sumatera Selatan"
DEFAULT_DESCRIPTION = "Website resmi DPW ABI Sumatera Selatan"
DEFAULT_IMAGE = "https://farhansyihab.github.io/abi-firebase/public/img/icons/apple-touch-icon-180x180.png"
SITE_URL = "https://abi-sumsel.my.id"

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