import requests
import json

BASE_URL = "http://localhost:8000/api"

# 1. Check current product features
response = requests.get(f"{BASE_URL}/product_features/")
print(f"Product Features Status: {response.status_code}")
if response.status_code == 200:
    features = response.json()
    print(f"Number of product features: {len(features)}")
    if features:
        print(f"Example feature keys: {list(features[0]['features'].keys())}")
        print(f"Example feature dimensions: {len(features[0]['features'])}")

# 2. Test recommendation for a user
response = requests.get(f"{BASE_URL}/recommendations/for_user/?user_id=1&limit=5")
print(f"\nRecommendation Status: {response.status_code}")
print(f"Response: {json.dumps(response.json() if response.status_code == 200 else response.text, indent=2)}")

# 3. Check similar items
response = requests.get(f"{BASE_URL}/recommendations/similar_items/?product_id=67ed79e3e1d9088051060a82&limit=3")
print(f"\nSimilar Items Status: {response.status_code}")
print(f"Response: {json.dumps(response.json() if response.status_code == 200 else response.text, indent=2)}")