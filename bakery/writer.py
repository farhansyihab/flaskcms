"""
Writer HTML ke file system dengan struktur folder yang benar
ENHANCED: Better error handling and validation
"""
import shutil
import time
import json
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

    def copy_includes_files(self):
        """Copy include files ke output directory"""
        # Cari folder includes
        possible_include_dirs = [
            BakeryConfig.TEMPLATE_DIR / "public" / "includes",
            BakeryConfig.PROJECT_ROOT / "app" / "templates" / "public" / "includes",
            Path("app/templates/public/includes"),
            Path("templates/public/includes"),
        ]
        
        include_src = None
        for dir_path in possible_include_dirs:
            if dir_path.exists() and dir_path.is_dir():
                include_src = dir_path
                break
        
        if not include_src:
            print("⚠️  Includes directory not found")
            return
        
        include_dest = self.output_dir / "includes"
        
        # Hapus yang lama
        if include_dest.exists():
            shutil.rmtree(include_dest)
        
        # Copy yang baru
        try:
            shutil.copytree(include_src, include_dest)
            file_count = sum(1 for _ in include_dest.rglob("*") if _.is_file())
            print(f"📄 Copied {file_count} include files to {include_dest}")
        except Exception as e:
            print(f"❌ Error copying include files: {e}")            
    
    def generate_sitemap(self, urls):
        """Generate sitemap.xml dari semua URL - IMPROVED dengan priority berbeda"""
        if not urls:
            print("⚠️  No URLs for sitemap")
            return
        
        sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for url in urls:
            full_url = f"{BakeryConfig.SITE_URL}{url}"
            
            # Tentukan priority berdasarkan jenis halaman
            priority = "0.8"
            changefreq = "weekly"
            
            if url == "/":
                priority = "1.0"
                changefreq = "daily"
            elif url == "/info/":
                priority = "0.9"
                changefreq = "daily"
            elif url.startswith("/info/page/"):
                priority = "0.7"
                changefreq = "weekly"
            elif url.startswith("/info/"):
                priority = "0.8"
                changefreq = "monthly"
            elif url in ["/about/", "/team/", "/contact/"]:
                priority = "0.8"
                changefreq = "monthly"
            
            sitemap_content += f'  <url>\n'
            sitemap_content += f'    <loc>{full_url}</loc>\n'
            sitemap_content += f'    <changefreq>{changefreq}</changefreq>\n'
            sitemap_content += f'    <priority>{priority}</priority>\n'
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

    def generate_search_index(self, articles, pages):
        """Generate JSON index untuk client-side search - FIXED"""
        search_data = []
        
        # Tambahkan artikel
        for article in articles:
            search_data.append({
                "type": "article",
                "title": article.get("title", ""),
                "slug": f"/info/{article.get('slug', '')}/",
                "excerpt": article.get("excerpt", "")[:150],
                "content": article.get("content", "")[:500] if article.get("content") else "",
                "date": article.get("created_at", "")
            })
        
        # Tambahkan halaman statis (kecuali homepage dengan slug "/")
        for page in pages:
            slug = page.get("slug", "").strip()
            if slug and slug != "/":
                # Skip homepage yang sudah ditangani terpisah
                if slug == "/":
                    continue
                    
                search_data.append({
                    "type": "page",
                    "title": page.get("title", ""),
                    "slug": f"/{slug.strip('/')}/",
                    "excerpt": page.get("seo", {}).get("description", "")[:150],
                    "content": page.get("content_html", "")[:500] if page.get("content_html") else "",
                    "date": page.get("updated_at", "")
                })
        
        # Tulis ke file
        search_path = self.output_dir / "search.json"
        with open(search_path, 'w', encoding='utf-8') as f:
            json.dump(search_data, f, ensure_ascii=False, indent=2)
        
        print(f"🔍 Generated search.json with {len(search_data)} entries")

    def generate_rss_feed(self, articles):
        """Generate RSS feed XML dari artikel terbaru - SIMPLE"""
        if not articles:
            print("⚠️  No articles for RSS feed")
            return
        
        # Sort articles by date (newest first)
        sorted_articles = sorted(
            articles,
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        
        # Ambil 20 artikel terbaru (bisa disesuaikan)
        latest_articles = sorted_articles[:20]
        
        # Current time untuk timestamp
        from datetime import datetime
        current_time = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        # Build RSS content
        rss_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
    <title>DPW ABI Sumatera Selatan - Berita Terkini</title>
    <link>{BakeryConfig.SITE_URL}</link>
    <atom:link href="{BakeryConfig.SITE_URL}/feed.xml" rel="self" type="application/rss+xml" />
    <description>Website resmi DPW Ahlulbait Indonesia Sumatera Selatan - Kumpulan berita dan informasi terkini</description>
    <language>id</language>
    <lastBuildDate>{current_time}</lastBuildDate>
    <generator>FlaskCMS Bakery v1.0</generator>
    
'''
        
        # Add each article as item
        for article in latest_articles:
            # Prepare article data
            title = article.get("title", "Untitled")
            slug = article.get("slug", "")
            description = article.get("excerpt", article.get("meta_description", ""))
            content = article.get("content", "")
            author = article.get("author", "Admin")
            pub_date = article.get("created_at", "")
            
            # Format date for RSS
            try:
                if pub_date:
                    # Parse ISO format to RFC 822 format
                    from datetime import datetime
                    if "T" in pub_date:
                        dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                        pub_date_formatted = dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
                    else:
                        pub_date_formatted = pub_date
                else:
                    pub_date_formatted = current_time
            except:
                pub_date_formatted = current_time
            
            # Build item
            rss_content += f'''    <item>
        <title>{self.escape_xml(title)}</title>
        <link>{BakeryConfig.SITE_URL}/info/{slug}/</link>
        <guid isPermaLink="true">{BakeryConfig.SITE_URL}/info/{slug}/</guid>
        <description>{self.escape_xml(description[:200])}</description>
        <pubDate>{pub_date_formatted}</pubDate>
        <author>{self.escape_xml(author)}</author>
    </item>
'''
        
        # Close RSS
        rss_content += '</channel>\n</rss>'
        
        # Write to file
        rss_path = self.output_dir / "feed.xml"
        with open(rss_path, 'w', encoding='utf-8') as f:
            f.write(rss_content)
        
        print(f"📰 Generated RSS feed with {len(latest_articles)} articles")
    
    def escape_xml(self, text):
        """Escape XML special characters - SIMPLE"""
        if not text:
            return ""
        
        escapes = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&apos;'
        }
        
        for char, escape in escapes.items():
            text = text.replace(char, escape)
        
        return text