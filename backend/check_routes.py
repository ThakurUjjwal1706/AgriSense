import requests
import json

try:
    print("Fetching docs from .98...")
    response = requests.get('http://172.32.5.98:8000/openapi.json', timeout=5)
    data = response.json()
    paths = data.get("paths", {})
    
    print("All Available Routes on .98 backend:")
    for p, methods in paths.items():
        for method in methods.keys():
            print(f" -> [{method.upper()}] {p}")
except Exception as e:
    print(f"Failed: {e}")
