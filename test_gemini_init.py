"""
Quick test script for Gemini service
"""
import asyncio
import sys
sys.path.insert(0, 'e:\\projek_b\\fastapi-santri')

from app.services.gemini_service import GeminiService
from app.core.config import settings

async def test_gemini_init():
    """Test if Gemini service initializes correctly"""
    try:
        print("Testing Gemini Service initialization...")
        print(f"API Key configured: {settings.gemini_api_key is not None}")
        print(f"Model: {settings.gemini_model}")
        print(f"Temperature: {settings.gemini_temperature}")
        
        service = GeminiService()
        print("✓ Gemini Service initialized successfully!")
        print(f"✓ Using model: {service.model_name}")
        return True
    except Exception as e:
        print(f"✗ Error initializing Gemini Service: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_gemini_init())
    sys.exit(0 if result else 1)
