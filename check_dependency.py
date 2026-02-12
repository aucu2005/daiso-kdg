
import sys
import os

print(f"Python Version: {sys.version}")
print(f"Executable: {sys.executable}")

print("\n--- Checking Imports ---")
try:
    import audioop
    print("✅ import audioop: SUCCESS")
except ImportError as e:
    print(f"❌ import audioop: FAILED ({e})")

try:
    import pyaudioop
    print("✅ import pyaudioop: SUCCESS")
except ImportError as e:
    print(f"❌ import pyaudioop: FAILED ({e})")

try:
    from pydub import AudioSegment
    print("✅ import pydub: SUCCESS")
except ImportError as e:
    print(f"❌ import pydub: FAILED ({e})")
except Exception as e:
    print(f"❌ import pydub: CRASHED ({e})")

print("\n--- Try Install (Simulated) ---")
print("Try running: pip install pyaudioop")
