"""Base Firestore service with common utilities"""
import traceback
from google.cloud import firestore
from google.cloud.firestore_v1 import FieldFilter

_db = None

def get_db():
    """Get Firestore database instance (singleton)"""
    global _db
    if _db is None:
        _db = firestore.Client()
    return _db

def get_collection_stats():
    """Get statistics about collections"""
    db = get_db()
    stats = {}
    
    collections_to_check = ['pages', 'articles', 'users']
    
    for col_name in collections_to_check:
        try:
            docs = list(db.collection(col_name).limit(1000).stream())
            stats[col_name] = len(docs)
        except Exception:
            stats[col_name] = 0
    
    return stats

def safe_stream_query(collection, **filters):
    """Safe wrapper for Firestore streaming queries"""
    try:
        query = get_db().collection(collection)
        
        for field, condition in filters.items():
            if isinstance(condition, dict):
                for op, value in condition.items():
                    if op == "==":
                        query = query.where(filter=FieldFilter(field, "==", value))
                    elif op == "!=":
                        query = query.where(filter=FieldFilter(field, "!=", value))
                    # Add more operators as needed
            else:
                query = query.where(filter=FieldFilter(field, "==", condition))
        
        return query.stream()
    except Exception as e:
        print(f"❌ Error in query: {e}")
        traceback.print_exc()
        return iter([])