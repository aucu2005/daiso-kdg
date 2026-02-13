import sqlite3
import shutil
import os
import time

src = 'backend/database/products.db'
dst = 'backend/database/products_copy.db'

print(f"Copying {src} to {dst}...", flush=True)
try:
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print("Copy successful.", flush=True)
    else:
        print(f"Source DB not found: {src}", flush=True)
        exit(1)

    conn = sqlite3.connect(dst)
    cursor = conn.cursor()
    
    print("\n--- Map Zones ---", flush=True)
    cursor.execute("SELECT id, name, type, floor FROM map_zones")
    zones = cursor.fetchall()
    if zones:
        for z in zones:
            print(z, flush=True)
    else:
        print("No map zones found.", flush=True)
        
    conn.close()
    
except Exception as e:
    print(f"Error: {e}", flush=True)
finally:
    if os.path.exists(dst):
        try:
            os.remove(dst)
            print("Removed copy.", flush=True)
        except:
            pass
