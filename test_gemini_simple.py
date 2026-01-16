"""Simple test for Gemini service"""
import asyncio
from app.core.config import settings

print(f"Gemini API Key: {settings.gemini_api_key[:20]}..." if settings.gemini_api_key else "NOT SET")
print(f"Gemini Model: {settings.gemini_model}")
print(f"Gemini Temperature: {settings.gemini_temperature}")

try:
    from app.services.gemini_service import gemini_service
    print("\n✅ Gemini service imported successfully!")
except Exception as e:
    print(f"\n❌ Error importing gemini service: {e}")
    import traceback
    traceback.print_exc()
