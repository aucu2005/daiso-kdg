import sqlite3
import json
import os
import sys

# Add project root to path to allow imports from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database.database import get_connection
from backend.database.seed_map_zones import seed_zones

DB_PATH = os.path.join(os.path.dirname(__file__), 'products.db')
BACKUP_PATH = os.path.join(os.path.dirname(__file__), 'map_zones_backup.json')
LOG_PATH = os.path.join(os.path.dirname(__file__), 'reset_log.txt')

def log(message):
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode('utf-8', errors='ignore').decode('utf-8'))
        
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(str(message) + '\n')

def reset_zones():
    # Clear log file
    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        f.write("Starting Map Zone Reset...\n")

    if not os.path.exists(DB_PATH):
        log(f"❌ DB not found at {DB_PATH}")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 1. Backup existing zones
        cursor.execute("SELECT * FROM map_zones")
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        backup_data = []
        for row in rows:
            backup_data.append(dict(zip(columns, row)))
            
        with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        log(f"[BACKUP] Backed up {len(rows)} zones to {BACKUP_PATH}")

        # 2. Delete all zones
        cursor.execute("DELETE FROM map_zones")
        deleted_count = cursor.rowcount
        log(f"[DELETE] Deleted {deleted_count} zones from database")
        
        conn.commit()
        
        # 3. Re-seed zones
        # seed_zones() checks if zones exist and skips if they do. 
        # Since we deleted them, it should run.
        log("[SEED] Re-seeding zones...")
        seed_zones()
        
        # Verify seed count
        cursor.execute("SELECT COUNT(*) FROM map_zones")
        new_count = cursor.fetchone()[0]
        log(f"[SUCCESS] Reset complete. Current zone count: {new_count}")

    except Exception as e:
        log(f"[ERROR] Error during reset: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    reset_zones()
