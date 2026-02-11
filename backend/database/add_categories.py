import sqlite3
import os
import json

# Database paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'products.db')
POC_JSON_PATH = os.path.join(BASE_DIR, '..', 'poc', 'bjy', 'poc', 'data', 'poc_v6_mock_product_db.json')

def get_connection():
    return sqlite3.connect(DB_PATH)

def add_columns():
    conn = get_connection()
    cursor = conn.cursor()
    
    columns = [
        ("category_major", "TEXT"),
        ("category_middle", "TEXT"),
        ("floor", "TEXT"),
        ("location", "TEXT")
    ]
    
    for col_name, col_type in columns:
        try:
            cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}")
            print(f"✅ Added column: {col_name}")
        except sqlite3.OperationalError:
            print(f"ℹ️ Column {col_name} already exists")
        
    conn.commit()
    conn.close()

def update_from_json():
    if not os.path.exists(POC_JSON_PATH):
        print(f"❌ JSON file not found: {POC_JSON_PATH}")
        return

    with open(POC_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📦 Loaded {len(data)} products from JSON.")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    updated_count = 0
    
    for item in data:
        # Match by ID
        pid = item.get('id')
        category_major = item.get('category_major')
        category_middle = item.get('category_middle')
        floor = item.get('floor')
        location = item.get('location') # or shelf_id? item has both location and shelf_id. location seems to be shelf_id.
        
        # In JSON: "location": "BA01", "shelf_id": "BA01". They seem identical.
        
        cursor.execute("""
            UPDATE products 
            SET category_major = ?, category_middle = ?, floor = ?, location = ?
            WHERE id = ?
        """, (category_major, category_middle, floor, location, pid))
        
        if cursor.rowcount > 0:
            updated_count += 1
        else:
            # Optional: Insert if not exists? For now, we only update.
            pass
            
    conn.commit()
    conn.close()
    print(f"✅ Updated {updated_count} products from JSON.")

if __name__ == "__main__":
    add_columns()
    update_from_json()
