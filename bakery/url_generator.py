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
            # Coba path relatif dari current directory
            current_dir = Path.cwd()
            
            # Cek beberapa lokasi kemungkinan backup
            possible_backup_locations = [
                current_dir / "backups" / "latest_backup.txt",
                current_dir.parent / "backups" / "latest_backup.txt",
                BakeryConfig.CURRENT_DIR / "backups" / "latest_backup.txt",
                BakeryConfig.PROJECT_ROOT / "backups" / "latest_backup.txt",
            ]
            
            for backup_path in possible_backup_locations:
                if backup_path.exists():
                    print(f"📂 Found latest_backup.txt: {backup_path}")
                    # Baca isi file
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse file path dari content
                    lines = content.strip().split('\n')
                    for line in lines:
                        if line.startswith('File:'):
                            file_path = line.replace('File:', '').strip()
                            # Coba beberapa lokasi untuk file JSON
                            possible_json_locations = [
                                Path(file_path),
                                backup_path.parent / Path(file_path).name,
                                current_dir / "backups" / Path(file_path).name,
                                current_dir.parent / "backups" / Path(file_path).name,
                            ]
                            
                            for json_path in possible_json_locations:
                                if json_path.exists():
                                    print(f"📂 Found backup file: {json_path}")
                                    return json_path
            
            # Fallback: cari file JSON di direktori backups
            possible_backup_dirs = [
                current_dir / "backups",
                current_dir.parent / "backups",
                BakeryConfig.CURRENT_DIR / "backups",
                BakeryConfig.PROJECT_ROOT / "backups",
            ]
            
            for backup_dir in possible_backup_dirs:
                if backup_dir.exists():
                    backups = list(backup_dir.glob("*.json"))
                    if backups:
                        # Dapatkan backup terbaru
                        latest = max(backups, key=lambda x: x.stat().st_mtime)
                        print(f"📂 Using latest JSON backup: {latest}")
                        return latest
                        
        except Exception as e:
            print(f"⚠️  Error reading backup files: {e}")
        
        # Fallback ke file spesifik
        specific_backup = Path("backups/firestore_backup_20260101_061004.json")
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
                        "content_html": data.get("content_html", ""),  # Perhatikan field ini
                        "content": data.get("content_html", ""),  # Fallback
                        "seo": data.get("seo", {}),
                        "meta_description": data.get("meta_description", ""),
                        "author": data.get("author", ""),
                        "updated_at": doc.get("update_time", ""),
                    }
                    # DEBUG: Print page info
                    print(f"📄 Page found: '{page['title']}' (slug: '{page['slug']}', has content: {bool(page['content_html'])})")
                    pages.append(page)
        
        print(f"📄 Total published pages: {len(pages)}")
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
        """Generate semua URL yang akan di-bake - DENGAN PAGINATION"""
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
        
        # 4. Pagination URLs (NEW!)
        articles_per_page = 10
        total_articles = len(articles)
        total_pages = (total_articles + articles_per_page - 1) // articles_per_page
        
        # Sort articles by date (newest first)
        sorted_articles = sorted(
            articles, 
            key=lambda x: x.get("created_at", ""), 
            reverse=True
        )
        
        # Simpan untuk digunakan nanti
        self.sorted_articles = sorted_articles
        
        # Generate pagination URLs
        for page_num in range(1, total_pages + 1):
            if page_num == 1:
                # Page 1 sudah ada di /info/
                continue
            urls.append(f"/info/page/{page_num}/")
        
        print(f"➕ {total_pages - 1} pagination URLs (total {total_pages} pages)")
        
        # Remove duplicates and sort
        urls = sorted(set(urls))
        print(f"📊 Total unique URLs: {len(urls)}")
        
        return urls
    
    def get_data_for_url(self, url):
        """Ambil data spesifik untuk URL tertentu - DENGAN CLEAN DESCRIPTION"""
        url = url.rstrip('/')
        
        # Debug info
        print(f"🔍 Getting data for: {url}")
        
        # Halaman search
        if url == "/search":
            print("✅ Search page requested")
            return {
                "page": {
                    "title": "Pencarian - DPW ABI Sumatera Selatan",
                    "seo": {
                        "title": "Pencarian - DPW ABI Sumatera Selatan",
                        "description": "Cari artikel dan halaman di website DPW ABI Sumatera Selatan"
                    }
                }
            }
        
        # Article list dengan pagination
        if url == "/info" or url.startswith("/info/page/"):
            if not hasattr(self, 'sorted_articles'):
                articles = self.get_published_articles()
                self.sorted_articles = sorted(
                    articles, 
                    key=lambda x: x.get("created_at", ""), 
                    reverse=True
                )
            
            articles_per_page = 10
            total_articles = len(self.sorted_articles)
            total_pages = (total_articles + articles_per_page - 1) // articles_per_page
            
            # Tentukan halaman saat ini
            current_page = 1
            if url.startswith("/info/page/"):
                try:
                    current_page = int(url.replace("/info/page/", "").strip("/"))
                except:
                    current_page = 1
            
            # Validasi halaman
            if current_page < 1 or current_page > total_pages:
                print(f"❌ Invalid page number: {current_page}")
                return None
            
            # Hitung start dan end index
            start_idx = (current_page - 1) * articles_per_page
            end_idx = start_idx + articles_per_page
            
            # Ambil artikel untuk halaman ini
            page_articles = self.sorted_articles[start_idx:end_idx]
            
            # Info pagination
            pagination_info = {
                "current_page": current_page,
                "total_pages": total_pages,
                "total_articles": total_articles,
                "has_previous": current_page > 1,
                "has_next": current_page < total_pages,
                "previous_page": current_page - 1 if current_page > 1 else None,
                "next_page": current_page + 1 if current_page < total_pages else None,
                "page_numbers": self.get_page_numbers(current_page, total_pages)
            }
            
            # SEO untuk setiap halaman
            if current_page == 1:
                seo_title = "Info & Berita - DPW ABI Sumatera Selatan"
                seo_description = "Kumpulan berita dan informasi terkini dari DPW ABI Sumatera Selatan"
            else:
                seo_title = f"Info & Berita - Halaman {current_page} - DPW ABI Sumatera Selatan"
                seo_description = f"Halaman {current_page} dari berita dan informasi DPW ABI Sumatera Selatan"
            
            return {
                "articles": page_articles,
                "pagination": pagination_info,
                "page": {
                    "title": f"Info & Berita - Halaman {current_page}",
                    "seo": {
                        "title": seo_title,
                        "description": seo_description,
                        "image": BakeryConfig.DEFAULT_IMAGE,
                        "og_title": seo_title,
                        "og_description": seo_description,
                        "og_image": BakeryConfig.DEFAULT_IMAGE,
                        "twitter_card": "summary_large_image",
                        "twitter_title": seo_title,
                        "twitter_description": seo_description,
                        "twitter_image": BakeryConfig.DEFAULT_IMAGE
                    }
                }
            }
        
        # Article detail
        if url.startswith("/info/"):
            if not url.startswith("/info/page/"):
                slug = url.replace("/info/", "").strip("/")
                articles = self.get_published_articles()
                for article in articles:
                    if article.get("slug") == slug:
                        print(f"✅ Found article: {article.get('title')}")
                        
                        # **BERSIHKAN DESKRIPSI**
                        if article.get("excerpt"):
                            article["excerpt"] = self.clean_text(article["excerpt"], 300)
                        if article.get("meta_description"):
                            article["meta_description"] = self.clean_text(article["meta_description"], 160)
                        
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
    
    # Tambahkan method ini di dalam class URLGenerator

    def clean_text(self, text, max_length=None):
        """Bersihkan teks dari spasi berlebih dan newlines"""
        if not text:
            return ""
        
        import re
        
        # Ganti multiple newlines dan spasi dengan single space
        cleaned = re.sub(r'\s+', ' ', text)
        
        # Trim
        cleaned = cleaned.strip()
        
        # Potong jika diperlukan
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length].rsplit(' ', 1)[0] + '...'
        
        return cleaned

    def get_page_numbers(self, current_page, total_pages):
        """Generate list page numbers untuk pagination UI"""
        max_pages_to_show = 5
        half = max_pages_to_show // 2
        
        start = max(1, current_page - half)
        end = min(total_pages, start + max_pages_to_show - 1)
        
        # Adjust jika tidak cukup page
        if end - start + 1 < max_pages_to_show:
            start = max(1, end - max_pages_to_show + 1)
        
        return list(range(start, end + 1))