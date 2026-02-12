import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

try:
    print("Checking imports...")
    from backend.database.database import get_product_by_id
    print("✅ get_product_by_id imported successfully")
    
    from backend.navigation.pathfinder import MapNavigator
    print("✅ MapNavigator imported successfully")
    
    import backend.api
    print("✅ backend.api imported successfully")
    
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"❌ Import failed: {e}")
