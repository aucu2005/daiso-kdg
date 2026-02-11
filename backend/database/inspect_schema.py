import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'products.db')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'schema_info.txt')

def inspect_schema():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"Connecting to database at: {DB_PATH}\n")
        if not os.path.exists(DB_PATH):
            f.write("Database file not found!\n")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='products'")
            schema = cursor.fetchone()
            if schema:
                f.write("Current Schema for 'products':\n")
                f.write(schema[0] + "\n")
            else:
                f.write("Table 'products' does not exist.\n")
                
            # Also check for 'map_zones' just in case
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='map_zones'")
            schema_zones = cursor.fetchone()
            if schema_zones:
                f.write("\nCurrent Schema for 'map_zones':\n")
                f.write(schema_zones[0] + "\n")

        except Exception as e:
            f.write(f"Error inspecting schema: {e}\n")
        finally:
            conn.close()
    
    print(f"Schema info written to {OUTPUT_FILE}")

if __name__ == "__main__":
    inspect_schema()
