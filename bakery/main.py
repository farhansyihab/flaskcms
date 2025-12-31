"""
Main entry point untuk FlaskCMS Bakery
"""
import time
from bakery.config import BakeryConfig
from bakery.url_generator import URLGenerator
from bakery.renderer import TemplateRenderer
from bakery.writer import HTMLWriter

class FlaskCMSBakery:
    """Main bakery system untuk FlaskCMS"""
    
    def __init__(self, backup_file=None):
        self.config = BakeryConfig()
        self.url_gen = URLGenerator(backup_file)
        self.renderer = TemplateRenderer()
        self.writer = HTMLWriter()
        
    def run(self):
        """Jalankan proses baking"""
        print("=" * 50)
        print("🚀 FlaskCMS Bakery System")
        print("=" * 50)
        
        start_time = time.time()
        
        # Setup directories
        self.config.setup_dirs()
        
        # 1. Generate semua URL
        print("\n📋 Step 1: Generating URLs...")
        urls = self.url_gen.generate_all_urls()
        
        # 2. Render setiap URL
        print("\n🎨 Step 2: Rendering templates...")
        for url in urls:
            try:
                print(f"  Rendering: {url}")
                
                # Get data for this URL
                context_data = self.url_gen.get_data_for_url(url)
                
                if context_data is None:
                    print(f"  ⚠️ No data for {url}, skipping...")
                    continue
                
                # Render HTML
                html = self.renderer.render_url(url, context_data)
                
                # Write to file
                self.writer.write_html(url, html)
                
            except Exception as e:
                print(f"  ❌ Error rendering {url}: {e}")
                import traceback
                traceback.print_exc()
        
        # 3. Copy static files
        print("\n📁 Step 3: Copying static files...")
        self.writer.copy_static_files()
        
        # 4. Generate SEO files
        print("\n🔍 Step 4: Generating SEO files...")
        self.writer.generate_sitemap(urls)
        self.writer.generate_robots_txt()
        
        # 5. Summary
        elapsed = time.time() - start_time
        print("\n" + "=" * 50)
        print("✅ Bakery process completed!")
        print(f"⏱️  Time elapsed: {elapsed:.2f} seconds")
        print(f"📄 Total pages generated: {len(urls)}")
        print(f"📦 Output directory: {self.config.OUTPUT_DIR}")
        print("=" * 50)
        
        # Show some example files
        print("\n📋 Sample generated files:")
        sample_files = list(self.config.OUTPUT_DIR.glob("**/*.html"))[:5]
        for f in sample_files:
            rel_path = f.relative_to(self.config.OUTPUT_DIR)
            print(f"  • {rel_path}")

def main():
    """Entry point utama"""
    bakery = FlaskCMSBakery()
    bakery.run()

if __name__ == "__main__":
    main()