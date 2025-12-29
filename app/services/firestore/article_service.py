"""Article-related Firestore services"""
from .base_service import get_db
from google.cloud import firestore
from google.cloud.firestore_v1 import FieldFilter

# ===== Article Services =====

def get_published_articles(limit=10):
    """Get published articles - SIMPLE VERSION tanpa order_by"""
    db = get_db()
    try:
        # Query sederhana tanpa order_by untuk hindari index
        docs = (
            db.collection("articles")
            .where(filter=FieldFilter("published", "==", True))
            .limit(limit)
            .stream()
        )
        
        # Konversi ke list dan sort manual di Python
        articles_list = []
        for doc in docs:
            article_data = doc.to_dict()
            article_data["id"] = doc.id
            articles_list.append(article_data)
        
        # Sort manual berdasarkan created_at (baru ke tertua)
        articles_list.sort(
            key=lambda x: x.get("created_at") or "", 
            reverse=True
        )
        
        print(f"✅ Loaded {len(articles_list)} articles (sorted locally)")
        return articles_list
        
    except Exception as e:
        print(f"⚠️ Articles error: {e}")
        import traceback
        traceback.print_exc()
        return []
    
def get_published_articles_generator(limit=10):
    """Generator version for compatibility"""
    articles = get_published_articles(limit)
    for article in articles:
        yield article    

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
        import traceback
        traceback.print_exc()
    
    return None

def create_article(data):
    """Create new article"""
    db = get_db()
    article_data = {
        "title": data.get("title", ""),
        "slug": data.get("slug", ""),
        "content": data.get("content", ""),
        "excerpt": data.get("excerpt", ""),
        "published": data.get("published", False),
        "author": data.get("author", ""),
        "created_at": data.get("created_at"),
        "meta_title": data.get("meta_title", ""),
        "meta_description": data.get("meta_description", ""),
        "meta_image": data.get("meta_image", "")
    }
    
    db.collection("articles").add(article_data)
    print(f"✅ Article created: {article_data['title']}")

def get_article_by_id(doc_id):
    """Get article by document ID"""
    try:
        db = get_db()
        doc = db.collection("articles").document(doc_id).get()
        if doc.exists:
            return doc
        return None
    except Exception as e:
        print(f"❌ Error getting article {doc_id}: {e}")
        import traceback
        traceback.print_exc()
        return None

def update_article(doc_id, data):
    """Update existing article"""
    try:
        db = get_db()
        db.collection("articles").document(doc_id).update(data)
        print(f"✅ Article {doc_id} updated")
        return True
    except Exception as e:
        print(f"❌ Error updating article {doc_id}: {e}")
        import traceback
        traceback.print_exc()
        return False

def delete_article(doc_id):
    """Delete article by ID"""
    try:
        db = get_db()
        db.collection("articles").document(doc_id).delete()
        print(f"✅ Article {doc_id} deleted")
        return True
    except Exception as e:
        print(f"❌ Error deleting article {doc_id}: {e}")
        import traceback
        traceback.print_exc()
        return False