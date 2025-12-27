import traceback
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
    try:
        db = get_db()
        print("🔍 Fetching pages from Firestore...")
        
        # Query SEDERHANA tanpa order_by dulu
        docs = db.collection("pages").stream()
        
        docs_list = list(docs)
        print(f"   Found {len(docs_list)} documents in 'pages' collection")
        
        if len(docs_list) == 0:
            # Debug: coba lihat semua collection dan dokumen
            print("   ⚠️ No documents found. Checking all collections...")
            for col in db.collections():
                col_docs = list(col.limit(5).stream())
                print(f"   Collection '{col.id}': {len(col_docs)} docs")
                for doc in col_docs:
                    print(f"      - {doc.id}: {list(doc.to_dict().keys())}")
        
        # Return iterator
        return iter(docs_list)
        
    except Exception as e:
        print(f"❌ Error in get_pages(): {e}")
        traceback.print_exc()
        return iter([])

def get_all_pages():
    """Get semua pages (versi debug-friendly)"""
    try:
        db = get_db()
        docs_ref = db.collection("pages").stream()
        
        pages = []
        for doc in docs_ref:
            page_data = doc.to_dict()
            page_data["id"] = doc.id
            
            # Tambahkan timestamp dokumen
            if hasattr(doc, 'create_time'):
                page_data["firestore_create_time"] = doc.create_time
            if hasattr(doc, 'update_time'):
                page_data["firestore_update_time"] = doc.update_time
            
            pages.append(page_data)
        
        print(f"✅ get_all_pages() found {len(pages)} pages")
        return pages
        
    except Exception as e:
        print(f"❌ Error in get_all_pages(): {e}")
        return []
    
def get_pages_generator():
    """Generator version for compatibility"""
    pages = get_all_pages()
    for page in pages:
        yield page

def get_page_by_slug(slug):
    """Get page by slug - untuk public access"""
    db = get_db()
    try:
        print(f"🔍 Looking for page with slug: '{slug}'")
        docs = (
            db.collection("pages")
            .where(filter=FieldFilter("slug", "==", slug))
            .where(filter=FieldFilter("published", "==", True))
            .limit(1)
            .stream()
        )
        
        docs_list = list(docs)
        print(f"   Found {len(docs_list)} documents for slug '{slug}'")
        
        for doc in docs_list:
            page_data = doc.to_dict()
            page_data["id"] = doc.id
            return page_data
        return None
        
    except Exception as e:
        print(f"⚠️ Error in get_page_by_slug: {e}")
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

# ===== Pages Services =====

def delete_page(doc_id):
    """Delete page by ID"""
    try:
        db = get_db()
        db.collection("pages").document(doc_id).delete()
        print(f"✅ Page {doc_id} deleted")
        return True
    except Exception as e:
        print(f"❌ Error deleting page {doc_id}: {e}")
        return False

def get_page_by_id(doc_id):
    """Get page by document ID"""
    try:
        db = get_db()
        doc = db.collection("pages").document(doc_id).get()
        if doc.exists:
            return doc
        else:
            print(f"⚠️ Page {doc_id} not found")
            return None
    except Exception as e:
        print(f"❌ Error getting page {doc_id}: {e}")
        return None

def update_page(doc_id, data):
    """Update existing page"""
    try:
        db = get_db()
        
        # Flatten nested fields (like seo.title)
        flat_data = {}
        for key, value in data.items():
            if '.' in key:
                # Handle nested field updates
                parts = key.split('.')
                if parts[0] not in flat_data:
                    flat_data[parts[0]] = {}
                flat_data[parts[0]][parts[1]] = value
            else:
                flat_data[key] = value
        
        flat_data["updated_at"] = datetime.utcnow()
        
        db.collection("pages").document(doc_id).update(flat_data)
        print(f"✅ Page {doc_id} updated")
        return True
    except Exception as e:
        print(f"❌ Error updating page {doc_id}: {e}")
        return False

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