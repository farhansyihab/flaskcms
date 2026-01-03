from flask import current_app, abort, send_from_directory
import os
from app.public import public_bp

@public_bp.route('/includes/<path:filename>')
def includes_files(filename):
    """Serve include files (header, footer, etc.)"""
    try:
        # Path ke folder includes
        includes_dir = os.path.join(
            current_app.root_path, 
            'templates', 
            'public', 
            'includes'
        )
        
        # Debug info
        print(f"🔍 Serving include file: {filename}")
        print(f"   Directory: {includes_dir}")
        print(f"   Full path: {os.path.join(includes_dir, filename)}")
        
        # Cek apakah file ada
        if not os.path.exists(os.path.join(includes_dir, filename)):
            print(f"❌ File not found: {filename}")
            abort(404)
        
        return send_from_directory(includes_dir, filename)
        
    except Exception as e:
        print(f"❌ Error serving include file {filename}: {e}")
        abort(404)