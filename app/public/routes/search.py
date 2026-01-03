from flask import render_template
from app.public import public_bp

# Default values untuk SEO
DEFAULT_IMAGE = "https://farhansyihab.github.io/abi-firebase/public/img/icons/apple-touch-icon-180x180.png"

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