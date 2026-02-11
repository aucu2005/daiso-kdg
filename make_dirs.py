import os

dirs = [
    "backend/navigation/grids"
]

for d in dirs:
    try:
        os.makedirs(d, exist_ok=True)
        print(f"✅ Created {d}")
    except Exception as e:
        print(f"❌ Failed to create {d}: {e}")
