
import sqlite3
import os
import sys

print("Starting SQLite Test...", flush=True)
try:
    db_path = "test.db"
    conn = sqlite3.connect(db_path)
    print("Connected.", flush=True)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)")
    print("Table created.", flush=True)
    cursor.execute("INSERT INTO test (name) VALUES ('test')")
    conn.commit()
    print("Inserted.", flush=True)
    cursor.execute("SELECT * FROM test")
    print(cursor.fetchall(), flush=True)
    conn.close()
    os.remove(db_path)
    print("Done.", flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)
