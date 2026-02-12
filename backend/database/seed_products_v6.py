import json
import os
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.database.database import insert_product, init_database

JSON_PATH = os.path.join(os.getcwd(), 'poc', 'bjy', 'poc', 'data', 'poc_v6_mock_product_db.json')

def seed_products():
    print(f"Reading data from: {JSON_PATH}")
    
    if not os.path.exists(JSON_PATH):
        print("❌ JSON file not found!")
        return

    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            products = json.load(f)
            
        print(f"Found {len(products)} products in JSON.")
        
        success_count = 0
        for p in products:
            # Check required fields and types
            try:
                # Rank is not in JSON, generate it or use ID
                rank = p.get('id', 0) 
                name = p.get('name')
                price = p.get('price', 0)
                
                # Image handling (mock for now or extract from JSON if available?)
                # JSON doesn't seem to have image_url, but crawler code uses it.
                # format: "image_url": p.get('image', '') in crawler
                # In JSON v6? let's check
                # JSON has: id, name, category, price, location, raw_detail_text...
                # No image_url.
                image_url = "" 
                image_name = f"{rank:03d}_{name[:10]}.jpg" # Mock
                
                category_major = p.get('category_major')
                category_middle = p.get('category_middle')
                shelf_id = p.get('shelf_id')
                floor = p.get('floor')
                
                # Insert into DB
                if insert_product(
                    rank=rank,
                    name=name,
                    price=price,
                    image_url=image_url,
                    image_name=image_name,
                    category_major=category_major,
                    category_middle=category_middle,
                    shelf_id=shelf_id,
                    floor=floor
                ):
                    success_count += 1
                    if success_count % 100 == 0:
                        print(f"Inserted {success_count} products...")
                        
            except Exception as e:
                print(f"Error inserting product {p.get('name')}: {e}")
                
        print(f"✅ Successfully seeded {success_count} products.")

    except Exception as e:
        print(f"❌ Error reading JSON: {e}")

if __name__ == "__main__":
    # Ensure DB is initialized (and columns added)
    init_database()
    seed_products()
