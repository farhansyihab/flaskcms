"""
Generate semua URL yang akan dibake dari data Firestore
"""
import json
from pathlib import Path
from bakery.config import BakeryConfig

class URLGenerator:
    """Generator URL untuk static site"""
    
    def __init__(self, backup_file=None):
        # Konversi ke Path jika backup_file adalah string
        if backup_file and isinstance(backup_file, str):
            self.backup_file = Path(backup_file)
        else:
            self.backup_file = backup_file or self.get_latest_backup()
        
        self.data = self.load_backup_data()
        
    def get_latest_backup(self):
        """Ambil file backup terbaru"""
        try:
            with open(BakeryConfig.LATEST_BACKUP, 'r') as f:
                backup_name = f.read().strip()
            backup_path = BakeryConfig.PROJECT_ROOT / "backups" / backup_name
            return backup_path
        except:
            # Fallback ke backup terakhir
            backup_dir = BakeryConfig.PROJECT_ROOT / "backups"
            backups = list(backup_dir.glob("*.json"))
            if backups:
                return max(backups, key=lambda x: x.stat().st_mtime)
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
        """Ambil semua published pages"""
        pages = []
        collection = BakeryConfig.COLLECTIONS["pages"]
        
        if collection in self.data:
            for doc_id, doc_data in self.data[collection].items():
                # Cek apakah published
                if doc_data.get("published") == True:
                    doc_data["id"] = doc_id
                    pages.append(doc_data)
        
        print(f"📄 Found {len(pages)} published pages")
        return pages
    
    def get_published_articles(self):
        """Ambil semua published articles"""
        articles = []
        collection = BakeryConfig.COLLECTIONS["articles"]
        
        if collection in self.data:
            for doc_id, doc_data in self.data[collection].items():
                # Cek apakah published
                if doc_data.get("published") == True:
                    doc_data["id"] = doc_id
                    articles.append(doc_data)
        
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
            if slug and slug != "/":
                urls.append(f"/{slug}/")
        
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
        """Ambil data spesifik untuk URL tertentu"""
        url = url.rstrip('/')
        
        # Homepage
        if url == "" or url == "/":
            pages = self.get_published_pages()
            home_page = next((p for p in pages if p.get("slug") == "/"), None)
            return {"page": home_page, "is_home": True}
        
        # Article detail
        if url.startswith("/info/"):
            slug = url.replace("/info/", "").strip("/")
            articles = self.get_published_articles()
            article = next((a for a in articles if a.get("slug") == slug), None)
            return {"article": article} if article else None
        
        # Page detail
        pages = self.get_published_pages()
        slug = url.strip("/")
        page = next((p for p in pages if p.get("slug") == slug), None)
        return {"page": page} if page else None
        
        # Article list
        if url == "/info":
            articles = self.get_published_articles()
            return {"articles": articles}
        
        return 