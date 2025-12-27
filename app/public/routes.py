from flask import Blueprint, render_template, abort
from app.services.firestore import (
    get_published_articles,
    get_article_by_slug,
)

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    articles = [doc.to_dict() for doc in get_published_articles()]
    return render_template(
        "public/info/index.html",
        articles=articles,
        seo={
            "title": "ABI Sumatera Selatan",
            "description": "Website resmi ABI Sumatera Selatan",
        },
    )


@public_bp.route("/info/<slug>")
def article_detail(slug):
    article = get_article_by_slug(slug)
    if not article:
        abort(404)

    return render_template(
        "public/info/article.html",
        article=article,
        seo={
            "title": article.get("meta_title", article["title"]),
            "description": article.get("meta_description", article["excerpt"]),
            "image": article.get("meta_image"),
        },
    )