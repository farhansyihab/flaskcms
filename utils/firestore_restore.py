#!/usr/bin/env python3
"""
Utility untuk restore data Firestore dari file JSON backup.
Penggunaan: python utils/firestore_restore.py backup_file.json
"""

import os
import json
import argparse
from datetime import datetime
from google.cloud import firestore
from google.cloud.firestore_v1 import SERVER_TIMESTAMP

def restore_from_backup(backup_file, dry_run=False, overwrite=False):
    """Restore data dari file backup"""
    print("=" * 60)
    print("🔄 FIRESTORE RESTORE UTILITY")
    print("=" * 60)
    
    if not os.path.exists(backup_file):
        print(f"❌ File backup tidak ditemukan: {backup_file}")
        return
    
    # Baca file backup
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        metadata = backup_data.get('metadata', {})
        data = backup_data.get('data', {})
        
        print(f"📂 File backup: {backup_file}")
        print(f"📊 Metadata: {json.dumps(metadata, indent=2)}")
        
    except Exception as e:
        print(f"❌ Gagal membaca file backup: {e}")
        return
    
    # Connect ke Firestore
    try:
        db = firestore.Client()
        print("✅ Terhubung ke Firestore")
    except Exception as e:
        print(f"❌ Gagal connect ke Firestore: {e}")
        return
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - Tidak akan menulis data")
    
    total_restored = 0
    total_skipped = 0
    total_errors = 0
    
    # Restore setiap collection
    for collection_name, docs in data.items():
        print(f"\n📦 Restore collection: {collection_name}")
        print(f"   Jumlah dokumen: {len(docs)}")
        
        collection_ref = db.collection(collection_name)
        
        for doc_id, doc_info in docs.items():
            doc_data = doc_info.get('data', {})
            
            # Cek apakah dokumen sudah ada
            existing_doc = collection_ref.document(doc_id).get()
            
            if existing_doc.exists and not overwrite:
                print(f"   ⚠️  Skip {doc_id} (sudah ada)")
                total_skipped += 1
                continue
            
            try:
                if not dry_run:
                    # Convert string timestamps back to datetime jika perlu
                    processed_data = {}
                    for key, value in doc_data.items():
                        if isinstance(value, str) and 'T' in value and ':' in value:
                            try:
                                # Coba parse sebagai datetime
                                processed_data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                            except:
                                processed_data[key] = value
                        else:
                            processed_data[key] = value
                    
                    # Tambahkan restore timestamp
                    processed_data['_restored_at'] = SERVER_TIMESTAMP
                    
                    # Write ke Firestore
                    collection_ref.document(doc_id).set(processed_data, merge=True)
                
                print(f"   ✅ Restore {doc_id}")
                total_restored += 1
                
            except Exception as e:
                print(f"   ❌ Error restore {doc_id}: {e}")
                total_errors += 1
    
    print(f"\n{'='*60}")
    print("📊 RESTORE SUMMARY:")
    print(f"   ✅ Restored: {total_restored}")
    print(f"   ⚠️  Skipped: {total_skipped}")
    print(f"   ❌ Errors: {total_errors}")
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - Tidak ada data yang ditulis")

def restore_to_collection(backup_file, target_collection, dry_run=False):
    """Restore data ke collection tertentu (untuk migrasi)"""
    print(f"🔄 Restore ke collection: {target_collection}")
    
    try:
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        db = firestore.Client()
        data = backup_data.get('data', {})
        
        total = 0
        for collection_name, docs in data.items():
            print(f"\nMigrasi dari {collection_name} ke {target_collection}")
            
            for doc_id, doc_info in docs.items():
                doc_data = doc_info.get('data', {})
                
                # Tambahkan metadata sumber
                doc_data['_source_collection'] = collection_name
                doc_data['_source_doc_id'] = doc_id
                doc_data['_migrated_at'] = SERVER_TIMESTAMP
                
                # Generate new ID atau gunakan yang lama
                new_doc_id = f"{collection_name}_{doc_id}"
                
                if not dry_run:
                    db.collection(target_collection).document(new_doc_id).set(doc_data)
                
                print(f"   ✅ {doc_id} -> {new_doc_id}")
                total += 1
        
        print(f"\n📊 Total migrated: {total}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def list_collections():
    """List semua collections di Firestore saat ini"""
    try:
        db = firestore.Client()
        collections = list(db.collections())
        
        print("📋 COLLECTIONS DI FIRESTORE:")
        print("-" * 60)
        
        for col in collections:
            # Hitung dokumen
            docs = list(col.limit(100).stream())
            print(f"📁 {col.id}: {len(docs)} dokumen")
            
            # Tampilkan 3 dokumen pertama
            for i, doc in enumerate(docs[:3]):
                data = doc.to_dict()
                print(f"     {i+1}. {doc.id}: {str(data)[:80]}...")
            if len(docs) > 3:
                print(f"     ... dan {len(docs)-3} lebih")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Firestore Restore Utility')
    parser.add_argument('backup_file', nargs='?', help='File backup JSON')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing documents')
    parser.add_argument('--to-collection', help='Restore ke collection tertentu')
    parser.add_argument('--list-collections', action='store_true', help='List collections')
    
    args = parser.parse_args()
    
    if args.list_collections:
        list_collections()
    elif args.backup_file:
        if args.to_collection:
            restore_to_collection(args.backup_file, args.to_collection, args.dry_run)
        else:
            restore_from_backup(args.backup_file, args.dry_run, args.overwrite)
    else:
        print("❌ Harap spesifikasikan file backup")
        print("   Contoh: python firestore_restore.py backups/firestore_backup_20251227_123456.json")

if __name__ == "__main__":
    main()