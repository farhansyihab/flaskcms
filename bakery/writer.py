"""
Writer HTML ke file system dengan struktur folder
"""
import shutil
from pathlib import Path
from bakery.config import BakeryConfig

class HTMLWriter:
    """Tulis HTML ke file system dengan struktur yang benar"""
    
    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir) if output_dir else BakeryConfig.OUTPUT_DIR
        
    def url_to_filepath(self, url):
        """Konversi URL ke path file"""
        # Normalize URL
        url = url.strip("/")
        
        if not url or url == "/":
            return self.output_dir / "index.html"
        
        # Buat folder + index.html
        return self.output_dir / url / "index.html"
    
    def write_html(self, url, html_content):
        """Tulis HTML content ke file"""
        filepath = self.url_to_filepath(url)
        
        # Buat parent directory jika belum ada
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Tulis file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Generated: {filepath.relative_to(self.output_dir)}")
        return filepath
    
    def copy_static_files(self):
        """Copy semua static files ke output directory"""
        static_src = BakeryConfig.STATIC_DIR
        static_dest = self.output_dir / "static"
        
        if static_src.exists():
            # Hapus yang lama
            if static_dest.exists():
                shutil.rmtree(static_dest)
            
            # Copy yang baru
            shutil.copytree(static_src, static_dest)
            print(f"📁 Copied static files to {static_dest}")
        else:
            print("⚠️ Static directory not found")
    
    def generate_sitemap(self, urls):
        """Generate sitemap.xml dari semua URL"""
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
        """Generate robots.txt"""
        robots_content = f"""User-agent: *
Allow: /

Sitemap: {BakeryConfig.SITE_URL}/sitemap.xml
"""
        robots_path = self.output_dir / "robots.txt"
        with open(robots_path, 'w', encoding='utf-8') as f:
            f.write(robots_content)
        
        print("🤖 Generated robots.txt")