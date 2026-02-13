import urllib.request
import json
import urllib.error

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

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers=headers)

try:
    print(f"Testing POST {url}...", flush=True)
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.getcode()}", flush=True)
        print(f"Response: {response.read().decode('utf-8')}", flush=True)
except urllib.error.HTTPError as e:
    print(f"Status Code: {e.code}", flush=True)
    print(f"Error Response: {e.read().decode('utf-8')}", flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)
