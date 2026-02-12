
import sys
import os
import sqlite3

# Add current directory to path
sys.path.append(os.getcwd())

from backend.database.database import get_product_count, get_all_categories, DB_PATH

def check_only():
    print(f"Checking DB at: {DB_PATH}")
    try:
        count = get_product_count()
        print(f"Current product count: {count}")
        
        categories = get_all_categories()
        print(f"Current categories: {categories}")
    except Exception as e:
        print(f"Error reading DB: {e}")

if __name__ == "__main__":
    check_only()
