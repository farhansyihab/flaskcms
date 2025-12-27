#!/bin/bash
# Shell script untuk backup Firestore
# Menggunakan cara yang sama dengan aplikasi Flask

set -e  # Exit on error

echo "🚀 Starting Firestore Backup..."
echo "================================"

# Aktifkan virtual environment jika ada
if [ -d "env" ]; then
    echo "Activating virtual environment..."
    source env/bin/activate
fi

# Cek apakah bisa import app
echo "Testing application imports..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from app.services.firestore import get_db
    db = get_db()
    print('✅ Success! Project:', db.project)
    
    # Test query
    cols = list(db.collections())
    print(f'Found {len(cols)} collections')
    for col in cols[:3]:
        print(f'  - {col.id}')
except Exception as e:
    print(f'❌ Failed: {e}')
    import traceback
    traceback.print_exc()
"

# Jalankan backup
echo ""
echo "Starting backup..."
python utils/firestore_backup.py --all

# List backups
echo ""
echo "📋 Latest backups:"
echo "------------------"
python utils/firestore_backup.py --list | head -20

echo ""
echo "✅ Backup completed!"
echo "Backups stored in: backups/"