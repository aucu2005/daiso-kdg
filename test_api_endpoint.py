
import urllib.request
import json
import traceback

try:
    print("Testing http://localhost:8000/api/categories ...")
    with urllib.request.urlopen("http://localhost:8000/api/categories") as response:
        data = json.load(response)
        print("Response Code:", response.getcode())
        print("Response Data:", json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print("Error:", e)
    traceback.print_exc()
