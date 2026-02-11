import sqlite3
import os

DB_PATH = 'backend/database/products.db'

print(f"Checking {DB_PATH}...")
if not os.path.exists(DB_PATH):
    print("DB file not found!")
    exit(1)

try:
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM map_zones")
    print(f"Count: {cursor.fetchone()[0]}")
    conn.close()
    print("Done.")
except Exception as e:
    print(f"Error: {e}")
