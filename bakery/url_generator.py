"""
Generate semua URL yang akan dibake dari data Firestore
FIXED: Compatible with Firestore backup structure
"""
import json
from pathlib import Path
from bakery.config import BakeryConfig

class URLGenerator:
    """Generator URL untuk static site - FIXED FOR FIRESTORE STRUCTURE"""
    
    def __init__(self, backup_file=None):
        # Konversi ke Path jika backup_file adalah string
        if backup_file and isinstance(backup_file, str):
            self.backup_file = Path(backup_file)
        else:
            self.backup_file = backup_file or self.get_latest_backup()
        
        self.data = self.load_backup_data()
        
    def get_latest_backup(self):
        """Ambil file backup terbaru - FIXED PARSING"""
        try:
            with open(BakeryConfig.LATEST_BACKUP, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse file path from content
            lines = content.strip().split('\n')
            for line in lines:
                if line.startswith('File:'):
                    # Extract file path
                    file_path = line.replace('File:', '').strip()
                    backup_path = Path(file_path)
                    if backup_path.exists():
                        print(f"📂 Found backup file from latest_backup.txt: {backup_path}")
                        return backup_path
            
            # Fallback: look for any JSON file in backups directory
            backup_dir = BakeryConfig.PROJECT_ROOT / "backups"
            if backup_dir.exists():
                backups = list(backup_dir.glob("*.json"))
                if backups:
                    # Get the most recent backup
                    latest = max(backups, key=lambda x: x.stat().st_mtime)
                    print(f"📂 Using latest backup file: {latest}")
                    return latest
                    
        except Exception as e:
            print(f"⚠️  Error reading latest_backup.txt: {e}")
        
        # Fallback to specific file if exists
        specific_backup = BakeryConfig.PROJECT_ROOT / "backups" / "firestore_backup_20260101_061004.json"
        if specific_backup.exists():
            print(f"📂 Using specific backup file: {specific_backup}")
            return specific_backup
        
        print("❌ No backup file found!")
        return None
    
    def load_backup_data(self):
        """Load data dari backup JSON"""
        if not self.backup_file or not self.backup_file.exists():
            print(f"❌ Backup file tidak ditemukan: {self.backup_file}")
            return {}
        
        print(f"📂 Loading backup: {self.backup_file.name}")
        with open(self.backup_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_published_pages(self):
        """Ambil semua published pages - FIXED FOR FIRESTORE STRUCTURE"""
        pages = []
        collection = BakeryConfig.COLLECTIONS["pages"]
        
        if collection in self.data.get("data", {}):
            for doc_id, doc in self.data["data"][collection].items():
                # Firestore structure: doc = {"id": "...", "data": {...}}
                data = doc.get("data", {})
                if data.get("published") is True:
                    page = {
                        "id": doc_id,
                        "slug": data.get("slug", "").strip(),
                        "title": data.get("title", "Untitled"),
                        "content": data.get("content_html", ""),
                        "seo": data.get("seo", {}),
                        "meta_description": data.get("meta_description", ""),
                        "author": data.get("author", ""),
                        "updated_at": doc.get("update_time", ""),
                    }
                    pages.append(page)
        
        print(f"📄 Found {len(pages)} published pages")
        return pages
    
    def get_published_articles(self):
        """Ambil semua published articles - FIXED FOR FIRESTORE STRUCTURE"""
        articles = []
        collection = BakeryConfig.COLLECTIONS["articles"]
        
        if collection in self.data.get("data", {}):
            for doc_id, doc in self.data["data"][collection].items():
                # Firestore structure: doc = {"id": "...", "data": {...}}
                data = doc.get("data", {})
                if data.get("published") is True:
                    article = {
                        "id": doc_id,
                        "slug": data.get("slug", "").strip(),
                        "title": data.get("title", "Untitled"),
                        "content": data.get("content", ""),
                        "excerpt": data.get("excerpt", ""),
                        "meta_title": data.get("meta_title", ""),
                        "meta_description": data.get("meta_description", ""),
                        "meta_image": data.get("meta_image", ""),
                        "author": data.get("author", ""),
                        "created_at": data.get("created_at", ""),
                        "seo": data.get("seo", {}),
                    }
                    articles.append(article)
        
        print(f"📰 Found {len(articles)} published articles")
        return articles
    
    def generate_all_urls(self):
        """Generate semua URL yang akan di-bake"""
        urls = []
        
        # 1. Static URLs
        urls.extend(BakeryConfig.STATIC_URLS)
        print(f"➕ {len(BakeryConfig.STATIC_URLS)} static URLs")
        
        # 2. Page URLs
        pages = self.get_published_pages()
        for page in pages:
            slug = page.get("slug", "").strip()
            if slug and slug not in ["/", ""]:
                # Normalize: ensure starts with / and ends with /
                if not slug.startswith("/"):
                    slug = "/" + slug
                if not slug.endswith("/"):
                    slug = slug + "/"
                urls.append(slug)
        
        print(f"➕ {len(pages)} page URLs")
        
        # 3. Article URLs
        articles = self.get_published_articles()
        for article in articles:
            slug = article.get("slug", "").strip()
            if slug:
                urls.append(f"/info/{slug}/")
        
        print(f"➕ {len(articles)} article URLs")
        
        # Remove duplicates and sort
        urls = sorted(set(urls))
        print(f"📊 Total unique URLs: {len(urls)}")
        
        return urls
    
    def get_data_for_url(self, url):
        """Ambil data spesifik untuk URL tertentu - FIXED"""
        url = url.rstrip('/')
        
        # Debug info
        print(f"🔍 Getting data for: {url}")
        
        # Article list page
        if url == "/info":
            articles = self.get_published_articles()
            return {
                "articles": articles,
                "page": {
                    "title": "Berita & Informasi",
                    "seo": {"title": "Berita ABI SUMSEL", "description": "Informasi terbaru dari DPW ABI Sumatera Selatan"}
                }
            }
        
        # Article detail
        if url.startswith("/info/"):
            slug = url.replace("/info/", "").strip("/")
            articles = self.get_published_articles()
            for article in articles:
                if article.get("slug") == slug:
                    print(f"✅ Found article: {article.get('title')}")
                    return {"article": article}
            print(f"❌ Article not found: {slug}")
            return None
        
        # Homepage
        if url == "" or url == "/":
            print("✅ Homepage requested")
            return {
                "page": {
                    "title": "DPW ABI SUMSEL",
                    "seo": {
                        "title": "DPW ABI Sumatera Selatan",
                        "description": "Website resmi DPW Ahlulbait Indonesia Sumatera Selatan"
                    }
                },
                "is_home": True
            }
        
        # Page detail
        pages = self.get_published_pages()
        slug = url.strip("/")
        for page in pages:
            if page.get("slug").strip("/") == slug:
                print(f"✅ Found page: {page.get('title')}")
                return {"page": page}
        
        print(f"❌ Page not found: {slug}")
        return None