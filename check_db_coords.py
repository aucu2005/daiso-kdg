import sqlite3
import os

DB_PATH = 'backend/database/products.db'

def check_coordinates():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, name, location_x, location_y FROM products WHERE location_x IS NOT NULL")
        rows = cursor.fetchall()
        
        if rows:
            print(f"Found {len(rows)} products with coordinates:")
            for row in rows[:5]:
                print(row)
        else:
            print("No products found with coordinates (location_x IS NOT NULL).")
            
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        print(f"Total products: {count}")

        print("\n--- Map Zones ---")
        cursor.execute("SELECT id, name, type, floor FROM map_zones")
        zones = cursor.fetchall()
        if zones:
            for z in zones:
                print(z)
        else:
            print("No map zones found.")

    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_coordinates()
