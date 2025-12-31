"""
Renderer template Flask ke HTML dengan context palsu
"""
from flask import Flask
from app import create_app
from bakery.config import BakeryConfig

class TemplateRenderer:
    """Render template Flask dalam mode bakery"""
    
    def __init__(self):
        self.app = self.create_bakery_app()
    
    def create_bakery_app(self):
        """Buat Flask app khusus untuk bakery"""
        app = create_app()
        
        # Konfigurasi khusus bakery
        app.config.update({
            "SERVER_NAME": "localhost",
            "APPLICATION_ROOT": "/",
            "PREFERRED_URL_SCHEME": "https",
            "BAKERY_MODE": True
        })
        
        return app
    
    def render_url(self, url, context_data=None):
        """Render URL tertentu ke HTML string"""
        with self.app.test_request_context(path=url):
            # Setup minimal context
            g = self.app.app_context().g
            
            # Determine which template to use
            if url == "/":
                template = "public/home.html"
            elif url.startswith("/info/") and "/" not in url[6:]:
                # Article detail
                template = "public/info/article.html"
            elif url == "/info/":
                # Article list
                template = "public/info/index.html"
            else:
                # Regular page
                template = "public/page.html"
            
            # Render template
            from flask import render_template
            html = render_template(
                template,
                **context_data if context_data else {}
            )
            
            return html
    
    def render_homepage(self, home_page_data):
        """Render homepage khusus"""
        with self.app.test_request_context(path="/"):
            from flask import render_template
            return render_template(
                "public/home.html",
                page=home_page_data,
                is_home=True
            )