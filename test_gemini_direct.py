"""Test Gemini API directly"""
import asyncio
from io import BytesIO
from PIL import Image

# Create a simple test image
img = Image.new('RGB', (100, 100), color='red')
img_bytes = BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

print("Testing Gemini API...")

try:
    from google import genai
    from google.genai import types
    from app.core.config import settings
    
    print(f"✅ Import successful")
    print(f"API Key: {settings.gemini_api_key[:20] if settings.gemini_api_key else 'NOT SET'}...")
    print(f"Model: {settings.gemini_model}")
    
    # Initialize client
    client = genai.Client(api_key=settings.gemini_api_key)
    print(f"✅ Client initialized")
    
    # Test simple text generation
    print("\nTesting text generation...")
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents="Say 'Hello World' in 3 words"
    )
    print(f"✅ Text response: {response.text}")
    
    # Test with image
    print("\nTesting image analysis...")
    img_data = img_bytes.getvalue()
    
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part(text="What color is this image?"),
                    types.Part(
                        inline_data=types.Blob(
                            mime_type="image/png",
                            data=img_data
                        )
                    )
                ]
            )
        ],
        config=types.GenerateContentConfig(
            temperature=0.4
        )
    )
    print(f"✅ Image analysis response: {response.text}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
