import sqlite3
import os

DB_PATH = 'backend/database/products.db'

def update_coordinates():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Test coordinates (approximate locations on B1/B2 maps)
    # Based on 863x1024 map size
    updates = [
        # ID, Floor, X, Y
        (1, 'B2', 200, 300),  # Example B2 location
        (2, 'B1', 400, 500),  # Example B1 location
        (3, 'B1', 600, 200),
        (4, 'B2', 300, 600),
        (5, 'B2', 500, 400)
    ]
    
    try:
        for pid, floor, x, y in updates:
            cursor.execute("""
                UPDATE products 
                SET floor = ?, location_x = ?, location_y = ? 
                WHERE id = ?
            """, (floor, x, y, pid))
            print(f"Updated product {pid}: Floor={floor}, X={x}, Y={y}")
            
        conn.commit()
        print("✅ Database updated successfully")

    except Exception as e:
        print(f"Error updating database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_coordinates()
