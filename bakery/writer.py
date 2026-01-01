"""
Writer HTML ke file system dengan struktur folder yang benar
ENHANCED: Better error handling and validation
"""
import shutil
import time
from pathlib import Path
from bakery.config import BakeryConfig

class HTMLWriter:
    """Tulis HTML ke file system dengan struktur yang benar - ENHANCED"""
    
    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir) if output_dir else BakeryConfig.OUTPUT_DIR
        
    def url_to_filepath(self, url):
        """Konversi URL ke path file - FIXED FOR EDGE CASES"""
        # Normalize URL
        url = url.strip("/")
        
        if not url or url == "/" or url == "":
            return self.output_dir / "index.html"
        
        # Special case: /info/ should be /info/index.html
        if url == "info":
            return self.output_dir / "info" / "index.html"
        
        # Buat folder + index.html
        return self.output_dir / url / "index.html"
    
    def write_html(self, url, html_content):
        """Tulis HTML content ke file - WITH VALIDATION"""
        if not html_content or len(html_content.strip()) < 50:
            print(f"⚠️  Warning: Very short HTML for {url} ({len(html_content)} chars)")
        
        filepath = self.url_to_filepath(url)
        
        # Buat parent directory jika belum ada
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure HTML has proper doctype
        if not html_content.strip().startswith("<!DOCTYPE"):
            html_content = f"<!DOCTYPE html>\n{html_content}"
        
        # Tulis file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Verify file was written
            if filepath.exists() and filepath.stat().st_size > 0:
                rel_path = filepath.relative_to(self.output_dir)
                size_kb = filepath.stat().st_size / 1024
                print(f"✅ Generated: {rel_path} ({size_kb:.1f} KB)")
                return filepath
            else:
                print(f"❌ Failed to write: {filepath}")
                return None
                
        except Exception as e:
            print(f"❌ Error writing {filepath}: {e}")
            return None
    
    def copy_static_files(self):
        """Copy semua static files ke output directory - WITH FALLBACK"""
        # Try multiple possible static directories
        possible_static_dirs = [
            BakeryConfig.STATIC_DIR,
            BakeryConfig.PROJECT_ROOT / "app" / "static",
            BakeryConfig.PROJECT_ROOT / "static",
            Path(".") / "app" / "static",
        ]
        
        static_src = None
        for dir_path in possible_static_dirs:
            if dir_path.exists() and dir_path.is_dir():
                static_src = dir_path
                break
        
        if not static_src:
            print("⚠️  Static directory not found in any location")
            # Create empty static directory
            static_dest = self.output_dir / "static"
            static_dest.mkdir(exist_ok=True, parents=True)
            (static_dest / ".keep").touch()  # Create empty file
            print(f"📁 Created empty static directory at {static_dest}")
            return
        
        static_dest = self.output_dir / "static"
        
        # Hapus yang lama
        if static_dest.exists():
            shutil.rmtree(static_dest)
        
        # Copy yang baru
        try:
            shutil.copytree(static_src, static_dest)
            # Count files
            file_count = sum(1 for _ in static_dest.rglob("*") if _.is_file())
            print(f"📁 Copied {file_count} static files to {static_dest}")
        except Exception as e:
            print(f"❌ Error copying static files: {e}")
    
    def generate_sitemap(self, urls):
        """Generate sitemap.xml dari semua URL - IMPROVED"""
        if not urls:
            print("⚠️  No URLs for sitemap")
            return
        
        sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for url in urls:
            full_url = f"{BakeryConfig.SITE_URL}{url}"
            sitemap_content += f'  <url>\n'
            sitemap_content += f'    <loc>{full_url}</loc>\n'
            sitemap_content += f'    <changefreq>weekly</changefreq>\n'
            sitemap_content += f'    <priority>0.8</priority>\n'
            sitemap_content += f'  </url>\n'
        
        sitemap_content += '</urlset>'
        
        sitemap_path = self.output_dir / "sitemap.xml"
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        
        print(f"🗺️ Generated sitemap.xml with {len(urls)} URLs")
    
    def generate_robots_txt(self):
        """Generate robots.txt - IMPROVED"""
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        robots_content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/

Sitemap: {BakeryConfig.SITE_URL}/sitemap.xml

# Generated by FlaskCMS Bakery
# Date: {current_time}
"""
        robots_path = self.output_dir / "robots.txt"
        with open(robots_path, 'w', encoding='utf-8') as f:
            f.write(robots_content)
        
        print("🤖 Generated robots.txt")