"""Test actual endpoint"""
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO

# Create a test image
img = Image.new('RGB', (300, 300), color='green')
img_bytes = BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)

# Test endpoint
url = "http://localhost:8000/gemini/analyze/image"

files = {
    'file': ('test.jpg', img_bytes, 'image/jpeg')
}

data = {
    'prompt': 'Berapa usia orang dalam foto ini? Berikan estimasi usia yang detail.'
}

print("Sending request...")
response = requests.post(url, files=files, data=data)

print(f"Status Code: {response.status_code}")
print(f"\nFull Response:")
print(response.json())

if response.status_code == 200:
    result = response.json()
    print(f"\n{'='*50}")
    print(f"SUCCESS!")
    print(f"{'='*50}")
    
    if 'data' in result:
        print(f"\nAnalysis Result:")
        print(result['data'].get('analysis', 'No analysis found'))
        print(f"\nModel: {result['data'].get('model')}")
        print(f"Filename: {result['data'].get('filename')}")
else:
    print(f"\nError: {response.text}")
