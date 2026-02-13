import requests
import json
import time

url = "http://localhost:8000/api/navigation/route"
payload = {
    "start_x": 50,
    "start_y": 90,
    "floor": "B1",
    "target_product_id": 1,
    "kiosk_id": "Kiosk 1"
}
headers = {
    "Content-Type": "application/json"
}

try:
    with open("test_result.txt", "w") as f:
        f.write(f"Testing POST {url}...\n")
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        f.write(f"Status Code: {response.status_code}\n")
        f.write(f"Response: {response.text}\n")
except Exception as e:
    with open("test_result.txt", "w") as f:
        f.write(f"Error: {e}\n")
