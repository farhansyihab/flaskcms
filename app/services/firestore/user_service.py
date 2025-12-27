"""User-related Firestore services"""
from datetime import datetime
from .base_service import get_db

# ===== User Services =====

def get_user_by_email(email):
    """Get user by email"""
    db = get_db()
    from google.cloud.firestore_v1 import FieldFilter
    
    docs = (
        db.collection("users")
        .where(filter=FieldFilter("email", "==", email))
        .limit(1)
        .stream()
    )
    for doc in docs:
        return doc.to_dict()
    return None

def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        db = get_db()
        doc = db.collection("users").document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"❌ Error getting user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_or_update_user(user_data):
    """Save or update user in Firestore"""
    try:
        db = get_db()
        user_id = user_data.get("id", user_data.get("sub"))
        
        user_ref = db.collection("users").document(user_id)
        
        # Prepare user data
        user_doc = {
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "picture": user_data.get("picture", ""),
            "provider": "google",
            "is_admin": user_data.get("is_admin", False),
            "role": "admin" if user_data.get("is_admin") else "user",
            "last_login": datetime.utcnow()
        }
        
        user_ref.set(user_doc, merge=True)
        print(f"✅ User saved/updated: {user_data['email']}")
        return True
    except Exception as e:
        print(f"⚠️ Firestore user save error: {e}")
        import traceback
        traceback.print_exc()
        return False

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

def get_all_users(limit=100):
    """Get all users (for admin panel)"""
    try:
        db = get_db()
        docs = db.collection("users").limit(limit).stream()
        
        users = []
        for doc in docs:
            user_data = doc.to_dict()
            user_data["id"] = doc.id
            users.append(user_data)
        
        return users
    except Exception as e:
        print(f"❌ Error getting users: {e}")
        import traceback
        traceback.print_exc()
        return []