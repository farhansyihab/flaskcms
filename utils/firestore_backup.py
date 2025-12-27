#!/usr/bin/env python3
"""
Utility untuk backup data Firestore ke file JSON.
Menggunakan cara yang sama dengan aplikasi Flask.
"""

import os
import json
import sys
from datetime import datetime

# Tambahkan path ke app agar bisa import modul Flask
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Gunakan cara yang sama dengan aplikasi
    from app.services.firestore import get_db
    print("✅ Menggunakan koneksi database dari aplikasi Flask")
except ImportError as e:
    print(f"❌ Tidak bisa import app: {e}")
    print("   Pastikan script dijalankan dari folder project yang benar")
    sys.exit(1)

def ensure_backup_dir():
    """Pastikan folder backup ada"""
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BACKUP_DIR = os.path.join(BASE_DIR, "backups")
    
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    return BACKUP_DIR

def backup_all():
    """Backup semua data Firestore"""
    print("=" * 60)
    print("🔥 FIRESTORE BACKUP UTILITY")
    print("=" * 60)
    
    backup_dir = ensure_backup_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"firestore_backup_{timestamp}.json")
    
    print(f"📁 Backup akan disimpan ke: {backup_file}")
    
    try:
        # Gunakan get_db() yang sama dengan aplikasi
        db = get_db()
        print(f"✅ Terhubung ke Firestore (Project: {db.project})")
        
        # Get semua collections
        collections = list(db.collections())
        print(f"📊 Ditemukan {len(collections)} collections:")
        for col in collections:
            print(f"  - {col.id}")
        
        # Backup data
        all_data = {}
        total_docs = 0
        
        for collection in collections:
            collection_name = collection.id
            print(f"\n📦 Backup collection: {collection_name}")
            
            all_data[collection_name] = {}
            doc_count = 0
            
            try:
                docs = db.collection(collection_name).stream()
                
                for doc in docs:
                    doc_data = doc.to_dict()
                    
                    # Convert timestamps to string
                    for key, value in doc_data.items():
                        if isinstance(value, datetime):
                            doc_data[key] = value.isoformat()
                        elif hasattr(value, '_reference_value'):  # Firestore Reference
                            doc_data[key] = str(value)
                    
                    all_data[collection_name][doc.id] = {
                        "id": doc.id,
                        "data": doc_data,
                        "create_time": doc.create_time.isoformat() if doc.create_time else None,
                        "update_time": doc.update_time.isoformat() if doc.update_time else None
                    }
                    doc_count += 1
                
                print(f"  ✅ {doc_count} dokumen tersimpan")
                total_docs += doc_count
                
            except Exception as e:
                print(f"  ❌ Error backup {collection_name}: {e}")
                continue
        
        # Simpan ke file
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "timestamp": timestamp,
                    "total_collections": len(collections),
                    "total_documents": total_docs,
                    "project_id": str(db.project),
                    "backup_version": "1.0"
                },
                "data": all_data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print("✅ BACKUP SELESAI!")
        print(f"📊 Statistik:")
        print(f"   - Total collections: {len(collections)}")
        print(f"   - Total documents: {total_docs}")
        print(f"   - File: {backup_file}")
        print(f"   - Size: {os.path.getsize(backup_file) / 1024:.2f} KB")
        
        # Buat file info
        info_file = os.path.join(backup_dir, "latest_backup.txt")
        with open(info_file, 'w') as f:
            f.write(f"Last backup: {datetime.now().isoformat()}\n")
            f.write(f"File: {backup_file}\n")
            f.write(f"Collections: {len(collections)}\n")
            f.write(f"Documents: {total_docs}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Backup gagal: {e}")
        import traceback
        traceback.print_exc()
        return False

def backup_collections(collection_names):
    """Backup hanya collections tertentu"""
    print(f"🔄 Backup collections: {collection_names}")
    
    backup_dir = ensure_backup_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"firestore_partial_{timestamp}.json")
    
    try:
        db = get_db()
        all_data = {}
        total_docs = 0
        
        for col_name in collection_names:
            print(f"\n📦 Backup collection: {col_name}")
            all_data[col_name] = {}
            doc_count = 0
            
            try:
                docs = db.collection(col_name).stream()
                
                for doc in docs:
                    doc_data = doc.to_dict()
                    
                    # Convert timestamps
                    for key, value in doc_data.items():
                        if isinstance(value, datetime):
                            doc_data[key] = value.isoformat()
                    
                    all_data[col_name][doc.id] = {
                        "id": doc.id,
                        "data": doc_data,
                        "create_time": doc.create_time.isoformat() if doc.create_time else None,
                        "update_time": doc.update_time.isoformat() if doc.update_time else None
                    }
                    doc_count += 1
                
                print(f"  ✅ {doc_count} dokumen tersimpan")
                total_docs += doc_count
                
            except Exception as e:
                print(f"  ❌ Error backup {col_name}: {e}")
                continue
        
        # Save
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "timestamp": timestamp,
                    "collections": collection_names,
                    "total_documents": total_docs,
                    "type": "partial"
                },
                "data": all_data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Partial backup selesai: {backup_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def list_backups():
    """List semua file backup"""
    backup_dir = ensure_backup_dir()
    
    if not os.path.exists(backup_dir):
        print("📁 Folder backup kosong")
        return
    
    backups = [f for f in os.listdir(backup_dir) if f.endswith('.json')]
    backups.sort(reverse=True)
    
    print("📋 DAFTAR BACKUP:")
    print("-" * 80)
    
    if not backups:
        print("Tidak ada backup")
        return
    
    for i, backup in enumerate(backups, 1):
        file_path = os.path.join(backup_dir, backup)
        size_kb = os.path.getsize(file_path) / 1024
        mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        print(f"{i:2}. {backup}")
        print(f"    Size: {size_kb:.1f} KB | Modified: {mtime.strftime('%Y-%m-%d %H:%M')}")
        
        # Baca metadata
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                meta = data.get('metadata', {})
                print(f"    Collections: {meta.get('total_collections', 'N/A')} | "
                      f"Documents: {meta.get('total_documents', 'N/A')}")
        except:
            pass
        
        print()

def test_connection():
    """Test koneksi database"""
    print("🧪 Testing database connection...")
    
    try:
        db = get_db()
        
        # Coba akses collections
        collections = list(db.collections())
        
        print(f"✅ Koneksi berhasil!")
        print(f"   Project: {db.project}")
        print(f"   Collections ditemukan: {len(collections)}")
        
        # Tampilkan collections dan jumlah dokumen
        for col in collections:
            docs = list(col.limit(100).stream())
            print(f"   - {col.id}: {len(docs)} dokumen")
        
        return True
        
    except Exception as e:
        print(f"❌ Koneksi gagal: {e}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Firestore Backup Utility')
    parser.add_argument('--all', action='store_true', help='Backup semua collections')
    parser.add_argument('--collections', nargs='+', help='Backup collections tertentu')
    parser.add_argument('--list', action='store_true', help='List semua backup')
    parser.add_argument('--test', action='store_true', help='Test koneksi database')
    
    args = parser.parse_args()
    
    if args.test:
        test_connection()
    elif args.list:
        list_backups()
    elif args.collections:
        backup_collections(args.collections)
    elif args.all:
        backup_all()
    else:
        # Default: test connection dulu
        if test_connection():
            print("\n💡 Gunakan salah satu opsi:")
            print("   --all               Backup semua data")
            print("   --collections A B   Backup collections tertentu")
            print("   --list              Lihat daftar backup")
            print("   --test              Test koneksi")
        else:
            print("\n❌ Tidak bisa connect ke database. Pastikan:")
            print("   1. Aplikasi Flask bisa running")
            print("   2. Service account credentials sudah benar")
            print("   3. File app/services/firestore.py ada")

if __name__ == "__main__":
    main()