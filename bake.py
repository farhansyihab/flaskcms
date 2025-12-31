#!/usr/bin/env python3
"""
Command line interface untuk FlaskCMS Bakery
"""
import argparse
from bakery import FlaskCMSBakery

def main():
    parser = argparse.ArgumentParser(description="FlaskCMS Bakery - Static Site Generator")
    parser.add_argument(
        "--backup", 
        "-b",
        help="Path ke file backup Firestore JSON"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="dist",
        help="Output directory (default: dist)"
    )
    
    args = parser.parse_args()
    
    # Jalankan bakery
    bakery = FlaskCMSBakery(backup_file=args.backup)
    bakery.run()

if __name__ == "__main__":
    main()