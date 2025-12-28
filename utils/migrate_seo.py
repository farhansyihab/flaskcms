#!/usr/bin/env python3
"""
Script migrasi SEO sederhana untuk halaman yang sudah ada
Jalankan sekali saja: python migrate_seo.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.firestore.base_service import get_db
from datetime import datetime

def migrate_existing_pages():
    """Tambahkan field SEO ke halaman yang sudah ada"""
    print("🔧 Memulai migrasi SEO untuk halaman yang sudah ada...")
    
    db = get_db()
    pages_ref = db.collection("pages").stream()
    
    migrated = 0
    for doc in pages_ref:
        try:
            page_data = doc.to_dict()
            
            # Skip jika sudah ada field SEO yang lengkap
            if "seo" in page_data and isinstance(page_data["seo"], dict):
                if "og_title" in page_data["seo"] and "twitter_card" in page_data["seo"]:
                    print(f"   ✓ {doc.id} sudah memiliki SEO lengkap")
                    continue
            
            # Update dengan struktur SEO baru
            update_data = {
                "seo.title": page_data.get("title", ""),
                "seo.description": page_data.get("seo", {}).get("description", "") if "seo" in page_data else "",
                "seo.image": page_data.get("seo", {}).get("image", "") if "seo" in page_data else "",
                "seo.og_title": page_data.get("title", ""),
                "seo.og_description": page_data.get("seo", {}).get("description", "") if "seo" in page_data else "",
                "seo.og_image": page_data.get("seo", {}).get("image", "") if "seo" in page_data else "",
                "seo.twitter_card": "summary_large_image",
                "seo.twitter_title": page_data.get("title", ""),
                "seo.twitter_description": page_data.get("seo", {}).get("description", "") if "seo" in page_data else "",
                "seo.twitter_image": page_data.get("seo", {}).get("image", "") if "seo" in page_data else "",
                "updated_at": datetime.utcnow()
            }
            
            # Tambahkan schema.org sederhana
            update_data["schema"] = {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": page_data.get("title", ""),
                "description": (page_data.get("seo", {}).get("description", "")[:160] 
                              if "seo" in page_data and page_data["seo"].get("description") 
                              else ""),
                "url": f"https://abisumsel.org/{page_data.get('slug', '')}" 
                      if page_data.get('slug') != '/' else "https://abisumsel.org",
                "publisher": {
                    "@type": "Organization",
                    "name": "DPW ABI Sumatera Selatan",
                    "url": "https://abisumsel.org"
                }
            }
            
            db.collection("pages").document(doc.id).update(update_data)
            migrated += 1
            print(f"   ✅ Migrasi berhasil: {page_data.get('title', doc.id)}")
            
        except Exception as e:
            print(f"   ❌ Error migrasi {doc.id}: {e}")
    
    print(f"\n📊 Migrasi selesai: {migrated} halaman diperbarui")
    return migrated

if __name__ == "__main__":
    migrate_existing_pages()
