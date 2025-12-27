#!/usr/bin/env python3
"""
Utility untuk inspect data Firestore.
"""

import os
from google.cloud import firestore
from tabulate import tabulate  # pip install tabulate

def inspect_collection(collection_name, limit=20):
    """Inspect isi collection"""
    print(f"\n🔍 INSPECT COLLECTION: {collection_name}")
    print("=" * 60)
    
    try:
        db = firestore.Client()
        docs = list(db.collection(collection_name).limit(limit).stream())
        
        if not docs:
            print("❌ Collection kosong")
            return
        
        print(f"📊 Jumlah dokumen: {len(docs)}")
        
        # Tampilkan sebagai tabel
        table_data = []
        for i, doc in enumerate(docs, 1):
            data = doc.to_dict()
            # Ambil beberapa field penting
            row = [
                i,
                doc.id,
                data.get('title', data.get('name', data.get('email', '-')))[:30],
                data.get('status', '-'),
                data.get('created_at', '-') if 'created_at' in data else '-',
                len(str(data))
            ]
            table_data.append(row)
        
        headers = ["#", "ID", "Title/Name", "Status", "Created", "Size"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Tampilkan contoh dokumen lengkap
        if docs:
            print(f"\n📄 Contoh dokumen pertama ({docs[0].id}):")
            print("-" * 60)
            import json
            print(json.dumps(docs[0].to_dict(), indent=2, default=str))
            
    except Exception as e:
        print(f"❌ Error: {e}")

def count_all_documents():
    """Hitung semua dokumen di semua collections"""
    print("\n📊 COUNT ALL DOCUMENTS")
    print("=" * 60)
    
    try:
        db = firestore.Client()
        collections = list(db.collections())
        
        total_docs = 0
        table_data = []
        
        for col in collections:
            # Count documents (ini bisa mahal untuk collection besar)
            docs = list(col.limit(1000).stream())
            count = len(docs)
            total_docs += count
            
            table_data.append([col.id, count])
        
        # Urutkan berdasarkan jumlah
        table_data.sort(key=lambda x: x[1], reverse=True)
        
        print(tabulate(table_data, headers=["Collection", "Documents"], tablefmt="grid"))
        print(f"\n📈 TOTAL: {total_docs} dokumen di {len(collections)} collections")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def export_schema():
    """Export schema/structure dari Firestore"""
    print("\n📋 FIRESTORE SCHEMA")
    print("=" * 60)
    
    try:
        db = firestore.Client()
        collections = list(db.collections())
        
        schema = {}
        
        for col in collections:
            docs = list(col.limit(5).stream())  # Sample beberapa dokumen
            fields = set()
            
            for doc in docs:
                fields.update(doc.to_dict().keys())
            
            schema[col.id] = {
                "sample_count": len(docs),
                "fields": sorted(list(fields)) if fields else []
            }
        
        # Print schema
        for col_name, col_info in schema.items():
            print(f"\n📁 {col_name}:")
            print(f"   Sample docs: {col_info['sample_count']}")
            if col_info['fields']:
                print(f"   Fields: {', '.join(col_info['fields'])}")
            else:
                print(f"   ⚠️  No documents found")
        
        # Save to file
        import json
        with open('firestore_schema.json', 'w') as f:
            json.dump(schema, f, indent=2)
        
        print(f"\n✅ Schema disimpan ke: firestore_schema.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Firestore Inspect Utility')
    parser.add_argument('--collection', help='Inspect collection tertentu')
    parser.add_argument('--count', action='store_true', help='Hitung semua dokumen')
    parser.add_argument('--schema', action='store_true', help='Export schema')
    parser.add_argument('--limit', type=int, default=20, help='Limit dokumen (default: 20)')
    
    args = parser.parse_args()
    
    if args.collection:
        inspect_collection(args.collection, args.limit)
    elif args.count:
        count_all_documents()
    elif args.schema:
        export_schema()
    else:
        print("❌ Pilih opsi:")
        print("   --collection NAMA_COLLECTION  # Inspect collection")
        print("   --count                       # Hitung semua dokumen")
        print("   --schema                      # Export schema")

if __name__ == "__main__":
    main()