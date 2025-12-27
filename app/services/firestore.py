from google.cloud import firestore
from datetime import datetime

_db = None


def get_db():
    global _db
    if _db is None:
        _db = firestore.Client()
    return _db


# ===== Article Services =====

def get_published_articles(limit=10):
    db = get_db()
    return (
        db.collection("articles")
        .where("status", "==", "published")
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )


def get_article_by_slug(slug):
    db = get_db()
    docs = (
        db.collection("articles")
        .where("slug", "==", slug)
        .limit(1)
        .stream()
    )
    for doc in docs:
        return doc.to_dict()
    return None


# ===== Pages Services =====

def get_pages():
    db = get_db()
    return (
        db.collection("pages")
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .stream()
    )


def get_page_by_id(doc_id):
    db = get_db()
    return db.collection("pages").document(doc_id).get()


def get_page_by_slug(slug):
    db = get_db()
    docs = (
        db.collection("pages")
        .where("slug", "==", slug)
        .where("status", "==", "published")
        .limit(1)
        .stream()
    )
    for doc in docs:
        return doc.to_dict()
    return None


def create_page(data):
    db = get_db()
    now = datetime.utcnow()
    data["created_at"] = now
    data["updated_at"] = now
    db.collection("pages").add(data)


def update_page(doc_id, data):
    db = get_db()
    data["updated_at"] = datetime.utcnow()
    db.collection("pages").document(doc_id).update(data)
