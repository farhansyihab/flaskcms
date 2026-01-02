"""
Main entry point untuk FlaskCMS Bakery - ENHANCED WITH DEBUG
"""
import time
import json
from pathlib import Path
from bakery.config import BakeryConfig
from bakery.url_generator import URLGenerator
from bakery.renderer import TemplateRenderer
from bakery.writer import HTMLWriter

class FlaskCMSBakery:
    """Main bakery system untuk FlaskCMS - WITH DEBUG INFO"""
    
    def __init__(self, backup_file=None):
        self.config = BakeryConfig()
        self.url_gen = URLGenerator(backup_file)
        self.renderer = TemplateRenderer()
        self.writer = HTMLWriter()
        
    def run(self):
        """Jalankan proses baking - WITH DEBUG"""
        print("=" * 60)
        print("🚀 FLASKCMS BAKERY SYSTEM - FIRESTORE COMPATIBLE")
        print("=" * 60)
        
        start_time = time.time()
        
        # Setup directories
        self.config.setup_dirs()
        
        # DEBUG: Show backup structure
        print("\n🔍 DEBUG: Backup Structure")
        print("-" * 40)
        if hasattr(self.url_gen, 'data') and self.url_gen.data:
            print(f"📊 Total collections in backup: {len(self.url_gen.data.get('data', {}))}")
            for collection_name in self.url_gen.data.get('data', {}):
                docs = self.url_gen.data['data'][collection_name]
                print(f"  • {collection_name}: {len(docs)} documents")
        
        # 1. Generate semua URL
        print("\n📋 Step 1: Generating URLs...")
        urls = self.url_gen.generate_all_urls()
        
        if not urls:
            print("❌ No URLs generated. Check backup file structure!")
            return
        
        # 2. Render setiap URL
        print("\n🎨 Step 2: Rendering templates...")
        successful = 0
        failed = 0
        
        for url in urls:
            try:
                print(f"\n🔗 Processing: {url}")
                
                # Get data for this URL
                context_data = self.url_gen.get_data_for_url(url)
                
                if context_data is None:
                    print(f"  ⚠️ No data for {url}, skipping...")
                    failed += 1
                    continue
                
                # Render HTML
                html = self.renderer.render_url(url, context_data)
                
                if not html:
                    print(f"  ❌ Empty HTML for {url}")
                    failed += 1
                    continue
                
                # Write to file
                output_path = self.writer.write_html(url, html)
                if output_path:
                    successful += 1
                
            except Exception as e:
                print(f"  ❌ Error processing {url}: {e}")
                import traceback
                traceback.print_exc()
                failed += 1
        
        # 3. Copy static files
        print("\n📁 Step 3: Copying static files...")
        self.writer.copy_static_files()
        self.writer.copy_includes_files()
        
        # 4. Generate SEO files
        print("\n🔍 Step 4: Generating SEO files...")
        self.writer.generate_sitemap(urls)
        self.writer.generate_robots_txt()

        # 5. Generate search index
        print("\n🔍 Step 5: Generating search index...")
        articles = self.url_gen.get_published_articles()
        pages = self.url_gen.get_published_pages()
        self.writer.generate_search_index(articles, pages)  

        # 6. Generate RSS feed
        print("\n📰 Step 6: Generating RSS feed...")
        if articles:
            self.writer.generate_rss_feed(articles)
        else:
            print("⚠️  No articles found for RSS feed")      
        
        # 7. Summary
        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print("✅ BAKERY PROCESS COMPLETED!")
        print("-" * 40)
        print(f"⏱️  Time elapsed: {elapsed:.2f} seconds")
        print(f"📄 Pages generated: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total URLs processed: {len(urls)}")
        print(f"📦 Output directory: {self.config.OUTPUT_DIR}")
        print("=" * 60)
        
        # Show generated files
        print("\n📋 Generated files:")
        html_files = list(self.config.OUTPUT_DIR.glob("**/*.html"))
        for f in html_files[:10]:  # Show first 10
            rel_path = f.relative_to(self.config.OUTPUT_DIR)
            size_kb = f.stat().st_size / 1024
            print(f"  • {rel_path} ({size_kb:.1f} KB)")
        
        if len(html_files) > 10:
            print(f"  ... and {len(html_files) - 10} more files")

def main():
    """Entry point utama"""
    bakery = FlaskCMSBakery()
    bakery.run()

if __name__ == "__main__":
    main()