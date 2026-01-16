"""Test upload like FastAPI does"""
import asyncio
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types
from app.core.config import settings

async def test_upload():
    # Create test image
    img = Image.new('RGB', (200, 200), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_data = img_bytes.getvalue()
    
    print(f"Image size: {len(img_data)} bytes")
    print(f"Using model: {settings.gemini_model}")
    
    client = genai.Client(api_key=settings.gemini_api_key)
    
    try:
        # Test exactly like service does
        prompt = "What color is this image?"
        
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type="image/jpeg",
                                data=img_data
                            )
                        )
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=settings.gemini_temperature
            )
        )
        
        print(f"✅ Success!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_upload())
