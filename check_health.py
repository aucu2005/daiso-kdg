import urllib.request
import urllib.error

url = "http://localhost:8000/health"

try:
    print(f"Testing GET {url}...", flush=True)
    with urllib.request.urlopen(url, timeout=2) as response:
        print(f"Status Code: {response.getcode()}", flush=True)
        print(f"Response: {response.read().decode('utf-8')}", flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)
