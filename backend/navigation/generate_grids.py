import os
import sys
# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.navigation.map_processor import MapProcessor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
FRONTEND_IMAGES_DIR = os.path.join(BASE_DIR, "frontend", "src", "assets", "images")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "grids")

def generate_grids():
    log_file = os.path.join(os.path.dirname(__file__), "grid_gen_log.txt")
    with open(log_file, "w", encoding="utf-8") as log:
        def log_print(msg):
            print(msg)
            log.write(msg + "\n")
            
        maps = [
            {"name": "b1", "filename": "map_b1.jpg"},
            {"name": "b2", "filename": "map_b2.jpg"}
        ]
        
        log_print(f"Base Dir: {BASE_DIR}")
        log_print(f"Images Dir: {FRONTEND_IMAGES_DIR}")
        log_print(f"Output Dir: {OUTPUT_DIR}")
        
        for m in maps:
            img_path = os.path.join(FRONTEND_IMAGES_DIR, m['filename'])
            output_path = os.path.join(OUTPUT_DIR, f"{m['name']}_grid.json")
            
            log_print(f"Processing {m['name']} map from {img_path}...")
            
            if not os.path.exists(img_path):
                log_print(f"❌ Image not found: {img_path}")
                continue
                
            try:
                # Grid size 10 means 1 pixel on grid = 10 pixels on map
                processor = MapProcessor(img_path, grid_size=10)
                processor.load_and_process()
                processor.save_grid(output_path)
                log_print(f"✅ Saved grid to {output_path}")
            except Exception as e:
                import traceback
                log_print(f"❌ Error processing {m['name']}: {e}")
                log_print(traceback.format_exc())

if __name__ == "__main__":
    generate_grids()
