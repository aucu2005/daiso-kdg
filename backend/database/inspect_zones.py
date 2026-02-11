import sqlite3
import json
import os
import sys

# Add backend to path to import database module if needed, but for inspection we can just use sqlite3 directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(os.path.dirname(__file__), 'products.db')
OUTPUT_FILE = 'inspection_result.txt'

def inspect():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        if not os.path.exists(DB_PATH):
            f.write(f"❌ DB not found at {DB_PATH}\n")
            return

        f.write(f"📂 Connecting to database at {DB_PATH}\n")
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check if map_zones table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='map_zones'")
            if not cursor.fetchone():
                f.write("❌ map_zones table does not exist\n")
                conn.close()
                return

            cursor.execute("SELECT id, floor, name, rect FROM map_zones ORDER BY floor, name")
            zones = cursor.fetchall()
            
            f.write(f"🔎 Found {len(zones)} zones:\n")
            
            # Group by floor and name to find duplicates
            zone_dict = {}
            
            for z in zones:
                zone_id, floor, name, rect = z
                key = (floor, name)
                if key not in zone_dict:
                    zone_dict[key] = []
                zone_dict[key].append(z)
                
                f.write(f"  ID: {zone_id}, Floor: {floor}, Name: {name}, Rect: {rect}\n")

            f.write("\n⚠️ Potential Duplicates:\n")
            has_duplicates = False
            for key, entries in zone_dict.items():
                if len(entries) > 1:
                    has_duplicates = True
                    f.write(f"  Floor: {key[0]}, Name: {key[1]} - {len(entries)} entries\n")
                    for entry in entries:
                        f.write(f"    ID: {entry[0]}, Rect: {entry[3]}\n")
            
            if not has_duplicates:
                f.write("  No obvious duplicates found by name.\n")
            
            conn.close()

        except Exception as e:
            f.write(f"❌ Error: {e}\n")

if __name__ == "__main__":
    inspect()
