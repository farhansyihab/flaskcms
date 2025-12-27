from google.cloud import firestore
from datetime import datetime
from google.cloud.firestore_v1 import FieldFilter

_db = None

def get_db():
    global _db
    if _db is None:
        _db = firestore.Client()
    return _db

# ===== Pages Services =====

def get_pages():
    """Get semua pages - untuk admin panel"""
    db = get_db()
    return (
        db.collection("pages")
        .order_by("create_time", direction=firestore.Query.DESCENDING)
        .stream()
    )

def get_page_by_slug(slug):
    """Get page by slug - untuk public access"""
    db = get_db()
    docs = (
        db.collection("pages")
        .where(filter=FieldFilter("slug", "==", slug))
        .where(filter=FieldFilter("published", "==", True))
        .limit(1)
        .stream()
    )
    for doc in docs:
        page_data = doc.to_dict()
        page_data["id"] = doc.id
        return page_data
    return None

def create_page(data):
    """Create new page"""
    db = get_db()
    
    page_data = {
        "title": data.get("title", ""),
        "slug": data.get("slug", ""),
        "content_html": data.get("content", ""),
        "published": data.get("status") == "published",
        "seo": {
            "title": data.get("meta_title", data.get("title", "")),
            "description": data.get("meta_description", ""),
            "image": data.get("meta_image", "")
        }
    }
    
    if "author" in data:
        page_data["author"] = data["author"]
    
    db.collection("pages").add(page_data)
    print(f"✅ Page created: {page_data['title']}")

def update_page(doc_id, data):
    """Update existing page"""
    db = get_db()
    data["updated_at"] = datetime.utcnow()
    db.collection("pages").document(doc_id).update(data)

def get_page_by_id(doc_id):
    """Get page by document ID"""
    db = get_db()
    return db.collection("pages").document(doc_id).get()

def get_home_page():
    """Get homepage - khusus untuk slug '/'"""
    db = get_db()
    docs = (
        db.collection("pages")
        .where(filter=FieldFilter("slug", "==", "/"))
        .where(filter=FieldFilter("published", "==", True))
        .limit(1)
        .stream()
    )
    
    for doc in docs:
        page_data = doc.to_dict()
        page_data["id"] = doc.id
        return page_data
    
    return None

def get_all_published_pages():
    """Get semua published pages untuk sitemap/menu"""
    db = get_db()
    return (
        db.collection("pages")
        .where(filter=FieldFilter("published", "==", True))
        .where(filter=FieldFilter("slug", "!=", "/"))
        .stream()
    )

# ===== Article Services =====

def get_published_articles(limit=10):
    """Get published articles"""
    db = get_db()
    try:
        return (
            db.collection("articles")
            .where(filter=FieldFilter("published", "==", True))
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
    except Exception as e:
        print(f"⚠️ Articles: {e}")
        return []

def get_article_by_slug(slug):
    """Get article by slug"""
    db = get_db()
    try:
        docs = (
            db.collection("articles")
            .where(filter=FieldFilter("slug", "==", slug))
            .limit(1)
            .stream()
        )
        for doc in docs:
            article_data = doc.to_dict()
            article_data["id"] = doc.id
            return article_data
    except Exception as e:
        print(f"⚠️ Error getting article: {e}")
    
    return None

# ===== User Services =====

def get_user_by_email(email):
    """Get user by email"""
    db = get_db()
    docs = (
        db.collection("users")
        .where(filter=FieldFilter("email", "==", email))
        .limit(1)
        .stream()
    )
    for doc in docs:
        return doc.to_dict()
    return None

def is_user_admin(user_id):
    """Check if user is admin"""
    db = get_db()
    user_doc = db.collection("users").document(user_id).get()
    
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return (
            user_data.get("role") == "admin" or
            user_data.get("is_admin") == True
        )
    
    return False

# ===== Helper Functions =====

def get_collection_stats():
    """Get statistics about collections"""
    db = get_db()
    stats = {}
    
    collections_to_check = ['pages', 'articles', 'users']
    
    for col_name in collections_to_check:
        try:
            docs = list(db.collection(col_name).limit(1000).stream())
            stats[col_name] = len(docs)
        except:
            stats[col_name] = 0
    
    return stats