"""
Konfigurasi untuk FlaskCMS Bakery System - FIXED PATHS
"""
import os
from pathlib import Path

class BakeryConfig:
    """Konfigurasi static site generator - FIXED PATHS"""
    
    # Fix: Use absolute paths from current directory
    CURRENT_DIR = Path.cwd()  # /home/farhan/Flask/flaskcms
    PROJECT_ROOT = CURRENT_DIR.parent  # /home/farhan/Flask
    
    # Template directory - check both relative and absolute
    TEMPLATE_DIR = PROJECT_ROOT / "templates"
    
    # Static directory
    STATIC_DIR = PROJECT_ROOT / "static"
    
    # Output directory
    OUTPUT_DIR = PROJECT_ROOT / "dist"
    
    # Backup directory
    BACKUP_DIR = PROJECT_ROOT / "backups"
    LATEST_BACKUP = BACKUP_DIR / "latest_backup.txt"
    
    # Specific backup file for testing
    SPECIFIC_BACKUP = BACKUP_DIR / "firestore_backup_20260101_061004.json"
    
    # URLs yang akan di-generate
    STATIC_URLS = [
        "/",                     # Home
        "/info/",                # Article list
        "/about/",               # About page
        "/contact/",             # Contact page
        "/team/",                # Team page
        "/search/",              # Search page
        "/jadwal-acara/",        # Schedule page
    ]
    
    # Nama collection di Firestore (from backup structure)
    COLLECTIONS = {
        "pages": "pages",
        "articles": "articles",
        "users": "users"
    }
    
    # Konfigurasi SEO
    SITE_URL = "https://abi-sumsel.my.id"
    DEFAULT_TITLE = "DPW ABI Sumatera Selatan"
    DEFAULT_DESCRIPTION = "Website resmi DPW Ahlulbait Indonesia Sumatera Selatan"
    
    @classmethod
    def setup_dirs(cls):
        """Setup directory output dengan validasi"""
        print(f"\n📁 Setting up directories...")
        print(f"  • Current dir: {cls.CURRENT_DIR}")
        print(f"  • Project root: {cls.PROJECT_ROOT}")
        
        # Create output directory
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        print(f"  • Output: {cls.OUTPUT_DIR}")
        
        # Create subdirectories
        (cls.OUTPUT_DIR / "static").mkdir(exist_ok=True)
        (cls.OUTPUT_DIR / "info").mkdir(exist_ok=True, parents=True)
        
        # Check if templates exist in app/templates or templates/
        if not cls.TEMPLATE_DIR.exists():
            print(f"⚠️  Template directory not found: {cls.TEMPLATE_DIR}")
            
            # Check app/templates
            app_templates = cls.PROJECT_ROOT / "app" / "templates"
            if app_templates.exists():
                cls.TEMPLATE_DIR = app_templates
                print(f"  ✅ Found templates in: {cls.TEMPLATE_DIR}")
            else:
                print(f"❌ Template directory not found anywhere!")
                # Create minimal template structure for testing
                cls.create_test_templates()
        
        # Check static directory
        if not cls.STATIC_DIR.exists():
            print(f"⚠️  Static directory not found: {cls.STATIC_DIR}")
            
            # Check app/static
            app_static = cls.PROJECT_ROOT / "app" / "static"
            if app_static.exists():
                cls.STATIC_DIR = app_static
                print(f"  ✅ Found static files in: {cls.STATIC_DIR}")
            else:
                print(f"⚠️  Static directory not found, will create empty")
    
    @classmethod
    def create_test_templates(cls):
        """Create minimal test templates if none exist"""
        templates_dir = cls.PROJECT_ROOT / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        # Create public directory
        public_dir = templates_dir / "public"
        public_dir.mkdir(exist_ok=True)
        
        # Create info directory
        info_dir = public_dir / "info"
        info_dir.mkdir(exist_ok=True)
        
        # Create minimal home.html
        home_template = public_dir / "home.html"
        if not home_template.exists():
            home_template.write_text("""
<!DOCTYPE html>
<html>
<head>
    <title>{{ page.title if page else 'Home' }}</title>
</head>
<body>
    <h1>{{ page.title if page else 'Welcome' }}</h1>
    {% if page.content %}
        {{ page.content|safe }}
    {% endif %}
</body>
</html>
""")
            print(f"  📄 Created test template: {home_template}")
        
        # Create minimal page.html
        page_template = public_dir / "page.html"
        if not page_template.exists():
            page_template.write_text("""
<!DOCTYPE html>
<html>
<head>
    <title>{{ page.title if page else 'Page' }}</title>
</head>
<body>
    <h1>{{ page.title if page else 'Page Title' }}</h1>
    {% if page.content %}
        {{ page.content|safe }}
    {% endif %}
</body>
</html>
""")
        
        # Create article.html
        article_template = info_dir / "article.html"
        if not article_template.exists():
            article_template.write_text("""
<!DOCTYPE html>
<html>
<head>
    <title>{{ article.title if article else 'Article' }}</title>
</head>
<body>
    {% if article %}
        <h1>{{ article.title }}</h1>
        <p><em>By {{ article.author }} on {{ article.created_at }}</em></p>
        {% if article.content %}
            {{ article.content|safe }}
        {% endif %}
    {% else %}
        <h1>Article not found</h1>
    {% endif %}
</body>
</html>
""")
        
        # Create index.html for articles list
        index_template = info_dir / "index.html"
        if not index_template.exists():
            index_template.write_text("""
<!DOCTYPE html>
<html>
<head>
    <title>{{ page.title if page else 'Articles' }}</title>
</head>
<body>
    <h1>{{ page.title if page else 'Articles' }}</h1>
    {% if articles %}
        <ul>
        {% for article in articles %}
            <li>
                <a href="/info/{{ article.slug }}/">{{ article.title }}</a>
                <p>{{ article.excerpt }}</p>
            </li>
        {% endfor %}
        </ul>
    {% else %}
        <p>No articles found.</p>
    {% endif %}
</body>
</html>
""")
        
        cls.TEMPLATE_DIR = templates_dir
        print(f"  ✅ Created test templates in: {cls.TEMPLATE_DIR}")