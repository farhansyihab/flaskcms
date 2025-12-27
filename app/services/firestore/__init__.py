"""Firestore services package"""
from .base_service import get_db, get_collection_stats
from .page_service import (
    get_pages, get_all_pages, get_pages_generator,
    get_page_by_slug, create_page, delete_page,
    get_page_by_id, update_page, get_home_page,
    get_all_published_pages
)
from .article_service import (
    get_published_articles, get_article_by_slug,
    create_article, get_article_by_id,
    update_article, delete_article
)
from .user_service import (
    get_user_by_email, get_user_by_id,
    save_or_update_user, is_user_admin,
    get_all_users
)

# For backward compatibility
__all__ = [
    # Base
    'get_db', 'get_collection_stats',
    
    # Pages
    'get_pages', 'get_all_pages', 'get_pages_generator',
    'get_page_by_slug', 'create_page', 'delete_page',
    'get_page_by_id', 'update_page', 'get_home_page',
    'get_all_published_pages',
    
    # Articles
    'get_published_articles', 'get_article_by_slug',
    'create_article', 'get_article_by_id',
    'update_article', 'delete_article',
    
    # Users
    'get_user_by_email', 'get_user_by_id',
    'save_or_update_user', 'is_user_admin',
    'get_all_users'
]