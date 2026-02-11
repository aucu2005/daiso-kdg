
import sqlite3
import json
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.database.database import get_connection, save_map_zone

# Data copied from mapZones.ts
B1_ZONES = [
    { 'name': '시즌', 'color': '#FFF9C4', 'floor': 'B1', 'rect': { 'left': '20%', 'top': '5%', 'width': '16%', 'height': '12.5%' } },
    { 'name': '화장품', 'color': '#FFE0E0', 'floor': 'B1', 'rect': { 'left': '38%', 'top': '5%', 'width': '16%', 'height': '12.5%' } },
    { 'name': '건강기능식품', 'color': '#E8F5E9', 'floor': 'B1', 'rect': { 'left': '20%', 'top': '20%', 'width': '16%', 'height': '12.5%' } },
    { 'name': '캐릭터', 'color': '#E3F2FD', 'floor': 'B1', 'rect': { 'left': '38%', 'top': '20%', 'width': '16%', 'height': '12.5%' } },
    { 'name': '문구', 'color': '#F3E5F5', 'floor': 'B1', 'rect': { 'left': '4%', 'top': '35%', 'width': '16%', 'height': '12.5%' } },
    { 'name': '파티·유아동', 'color': '#FFF3E0', 'floor': 'B1', 'rect': { 'left': '22%', 'top': '35%', 'width': '16%', 'height': '12.5%' } },
    { 'name': '패션', 'color': '#FFEBEE', 'floor': 'B1', 'rect': { 'left': '40%', 'top': '35%', 'width': '16%', 'height': '12.5%' } },
    { 'name': '포장', 'color': '#E1F5FE', 'floor': 'B1', 'rect': { 'left': '4%', 'top': '50%', 'width': '16%', 'height': '12.5%' } },
    { 'name': '디지털', 'color': '#E8EAF6', 'floor': 'B1', 'rect': { 'left': '22%', 'top': '50%', 'width': '16%', 'height': '12.5%' } },
    { 'name': '인테리어소품', 'color': '#FCE4EC', 'floor': 'B1', 'rect': { 'left': '40%', 'top': '50%', 'width': '16%', 'height': '12.5%' } },
    { 'name': '식품', 'color': '#FBE9E7', 'floor': 'B1', 'rect': { 'left': '40%', 'top': '65%', 'width': '16%', 'height': '12.5%' } },
]

B2_ZONES = [
    { 'name': '욕실', 'color': '#E1F5FE', 'floor': 'B2', 'rect': { 'left': '20%', 'top': '5%', 'width': '14%', 'height': '11%' } },
    { 'name': '청소', 'color': '#F3E5F5', 'floor': 'B2', 'rect': { 'left': '36%', 'top': '5%', 'width': '14%', 'height': '11%' } },
    { 'name': '세탁', 'color': '#FFF9C4', 'floor': 'B2', 'rect': { 'left': '52%', 'top': '5%', 'width': '14%', 'height': '11%' } },
    { 'name': '득템', 'color': '#E8F5E9', 'floor': 'B2', 'rect': { 'left': '68%', 'top': '5%', 'width': '14%', 'height': '11%' } },
    { 'name': '일본수입', 'color': '#FFE0B2', 'floor': 'B2', 'rect': { 'left': '20%', 'top': '19%', 'width': '14%', 'height': '11%' } },
    { 'name': 'ALL', 'color': '#FFEBEE', 'floor': 'B2', 'rect': { 'left': '36%', 'top': '19%', 'width': '14%', 'height': '11%' } },
    { 'name': '수납', 'color': '#F3E5F5', 'floor': 'B2', 'rect': { 'left': '52%', 'top': '19%', 'width': '14%', 'height': '11%' } },
    { 'name': '홈패브릭', 'color': '#E8F5E9', 'floor': 'B2', 'rect': { 'left': '4%', 'top': '32.5%', 'width': '14%', 'height': '11%' } },
    { 'name': '공구', 'color': '#FFF3E0', 'floor': 'B2', 'rect': { 'left': '20%', 'top': '32.5%', 'width': '14%', 'height': '11%' } },
    { 'name': '내추럴코너', 'color': '#E1F5FE', 'floor': 'B2', 'rect': { 'left': '36%', 'top': '32.5%', 'width': '14%', 'height': '11%' } },
    { 'name': '문구', 'color': '#FFEBEE', 'floor': 'B2', 'rect': { 'left': '52%', 'top': '32.5%', 'width': '14%', 'height': '11%' } },
    { 'name': '주방', 'color': '#FCE4EC', 'floor': 'B2', 'rect': { 'left': '68%', 'top': '32.5%', 'width': '14%', 'height': '11%' } },
    { 'name': '반려동물', 'color': '#F3E5F5', 'floor': 'B2', 'rect': { 'left': '4%', 'top': '46%', 'width': '14%', 'height': '11%' } },
    { 'name': '캠핑', 'color': '#FBE9E7', 'floor': 'B2', 'rect': { 'left': '20%', 'top': '46%', 'width': '14%', 'height': '11%' } },
    { 'name': '여행', 'color': '#E8EAF6', 'floor': 'B2', 'rect': { 'left': '36%', 'top': '46%', 'width': '14%', 'height': '11%' } },
    { 'name': '원예', 'color': '#C8E6C9', 'floor': 'B2', 'rect': { 'left': '52%', 'top': '46%', 'width': '14%', 'height': '11%' } },
]

def seed_zones():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if zones exist
    cursor.execute("SELECT COUNT(*) FROM map_zones")
    if cursor.fetchone()[0] > 0:
        print("⚠️ Map zones already exist. Skipping seed.")
        conn.close()
        return

    print("[SEED] Seeding map zones...")
    
    all_zones = B1_ZONES + B2_ZONES
    for zone in all_zones:
        rect_json = json.dumps(zone['rect'])
        cursor.execute(
            'INSERT INTO map_zones (floor, name, rect, color) VALUES (?, ?, ?, ?)',
            (zone['floor'], zone['name'], rect_json, zone['color'])
        )
    
    conn.commit()
    conn.close()
    print(f"[SUCCESS] Seeded {len(all_zones)} zones.")

if __name__ == "__main__":
    seed_zones()
