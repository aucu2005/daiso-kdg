
import sys
import time

print("--- Backend Startup Debugger ---")

def step(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}...", end="", flush=True)
    start = time.time()
    return start

def done(start):
    print(f" DONE ({time.time() - start:.2f}s)")

try:
    s = step("Importing os, sys, time")
    import os
    import sys
    import time
    done(s)

    s = step("Importing fastapi")
    from fastapi import FastAPI
    done(s)

    s = step("Importing backend.database.database")
    from backend.database.database import init_database
    done(s)

    s = step("Importing backend.navigation.pathfinder")
    from backend.navigation.pathfinder import MapNavigator
    done(s)

    s = step("Importing backend.stt (WhisperAdapter)")
    from backend.stt import WhisperAdapter
    done(s)

    s = step("Importing backend.api")
    import backend.api
    done(s)

    print("\n✅ Basic imports successful.")
    
    print("\n--- Testing Initializations ---")
    
    s = step("Initializing Database")
    init_database()
    done(s)

    s = step("Initializing MapNavigator")
    nav = MapNavigator()
    # Mock loading grid if needed, or just skip
    done(s)
    
    print("\n⚠️  If you see this, basic initialization worked.")
    print("If uvicorn hangs, it might be the server binding or model downloading.")
    
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

input("\nPress Enter to exit...")
