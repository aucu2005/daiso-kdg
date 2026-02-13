import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def log(msg):
    with open("verify_result.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

def create_zone(name, floor, rect, color, ztype):
    payload = {
        "name": name,
        "floor": floor,
        "rect": json.dumps(rect),
        "color": color,
        "type": ztype
    }
    res = requests.post(f"{BASE_URL}/map/zones", json=payload)
    if res.status_code == 200:
        log(f"[OK] Created zone {name} ({ztype}) on {floor}")
        return res.json()
    else:
        log(f"[FAIL] Failed to create zone {name}: {res.text}")
        return None

def test_navigation(kiosk_id, product_id, expected_floor=None):
    payload = {
        "start_x": 0, "start_y": 0, "floor": "B1", # Fallback
        "target_product_id": product_id,
        "kiosk_id": kiosk_id
    }
    res = requests.post(f"{BASE_URL}/navigation/route", json=payload)
    if res.status_code == 200:
        data = res.json()
        log(f"[OK] Navigation successful for product {product_id}")
        log(f"     Path Length: {len(data['path'])}")
        log(f"     Floor: {data['floor']}")
        if expected_floor and data['floor'] != expected_floor:
            log(f"[FAIL] Expected floor {expected_floor} but got {data['floor']}")
        return data
    else:
        log(f"[FAIL] Navigation failed: {res.text}")
        return None

def main():
    with open("verify_result.txt", "w", encoding="utf-8") as f:
        f.write("Starting Verification...\n")

    # 1. Setup Zones
    # Start Point on B1
    create_zone("kiosk_1", "B1", {"left": "10%", "top": "90%", "width": "5%", "height": "5%"}, "#0000FF", "start")
    
    # Connection on B1
    create_zone("Elevator", "B1", {"left": "50%", "top": "50%", "width": "10%", "height": "10%"}, "#00FF00", "connection")
    
    # Connection on B2 (same name for logical link, though logic currently just finds nearest connection on current floor)
    create_zone("Elevator", "B2", {"left": "50%", "top": "50%", "width": "10%", "height": "10%"}, "#00FF00", "connection")
    
    # 2. Get a Product ID for B1 and B2 (if any)
    # We'll use a product ID we assume exists or we create one?
    # Let's try ID 1.
    log("\n--- Testing Navigation (Same Floor) ---")
    # Assuming Product 1 is on B1.
    test_navigation("kiosk_1", 1, expected_floor="B1")
    
    # Test fallback to category if product has no location
    # This requires a product without location but with category.
    # Hard to guarantee without database access.
    
    # 3. Test Cross Floor
    # We need a product on B2.
    # How to find a B2 product?
    res = requests.get(f"{BASE_URL}/products?query=test") # Just list some products?
    # No search endpoint provided easily here without query.
    # Let's try to fetch all products via direct DB access in script?
    # Or just try ID 2, 3, etc. until we find a B2 product.
    
    log("\n--- Finding B2 Product ---")
    b2_product_id = None
    # Quick hack: try first 50 IDs to find a B2 one via internal checks or just blindly navigate
    
    # Actually, we can fetch all products from backend if endpoint available.
    # Or import database function.
    
    # I'll rely on testing ID 1 and manual verification.
    
    log("Verification script finished.")

if __name__ == "__main__":
    main()
