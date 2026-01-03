from flask import render_template, abort
from app.public import public_bp
from app.services.firestore import (
    get_published_articles, 
    get_article_by_slug
)

# Default values untuk SEO
DEFAULT_TITLE = "DPW ABI Sumatera Selatan"
DEFAULT_DESCRIPTION = "Website resmi DPW ABI Sumatera Selatan"
DEFAULT_IMAGE = "https://farhansyihab.github.io/abi-firebase/public/img/icons/apple-touch-icon-180x180.png"
SITE_URL = "https://abi-sumsel.my.id"

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
