"""
Konfigurasi untuk FlaskCMS Bakery System
"""
import os
from pathlib import Path

class BakeryConfig:
    """Konfigurasi static site generator"""
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    TEMPLATE_DIR = PROJECT_ROOT / "app" / "templates"
    STATIC_DIR = PROJECT_ROOT / "app" / "static"
    OUTPUT_DIR = PROJECT_ROOT / "dist"
    
    # File backup Firestore
    BACKUP_FILE = "firestore_backup.json"
    LATEST_BACKUP = PROJECT_ROOT / "backups" / "latest_backup.txt"
    
    # URLs yang akan di-generate
    STATIC_URLS = [
        "/",
        "/info/",
        "/about/",
        "/contact/",
        "/team/",
        "/search/"
    ]
    
    # Nama collection di Firestore
    COLLECTIONS = {
        "pages": "pages",
        "articles": "articles",
        "users": "users"
    }
    
    # Konfigurasi SEO
    SITE_URL = "https://abi-sumsel.my.id"
    DEFAULT_TITLE = "DPW ABI Sumatera Selatan"
    DEFAULT_DESCRIPTION = "Website resmi DPW ABI Sumatera Selatan"
    
    @classmethod
    def setup_dirs(cls):
        """Setup directory output"""
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        (cls.OUTPUT_DIR / "static").mkdir(exist_ok=True)
        (cls.OUTPUT_DIR / "info").mkdir(exist_ok=True, parents=True)
        
        print(f"📁 Output directory: {cls.OUTPUT_DIR}")