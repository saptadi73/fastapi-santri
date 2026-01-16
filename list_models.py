"""List available Gemini models"""
from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

print("Available models:")
try:
    models = client.models.list()
    for model in models:
        print(f"- {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"  Methods: {model.supported_generation_methods}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
