"""
list_available_models.py - See which models your API keys can actually access
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

print("="*70)
print("LISTING AVAILABLE MODELS FOR YOUR API KEYS")
print("="*70)
print()

# Load .env
config_dir = Path(__file__).parent / 'config'
env_path = config_dir / '.env'
load_dotenv(env_path)

# Get first API key
key1 = os.getenv('GOOGLE_API_KEY_1')

if not key1:
    print("❌ No API keys found in .env file!")
    exit()

print(f"Using API Key #1: {key1[:20]}...")
print()

try:
    # Create client
    client = genai.Client(api_key=key1)
    
    # List all available models
    print("Listing all available models...")
    print()
    
    models = client.models.list()
    
    print(f"Found {len(models)} models:")
    print()
    
    for model in models:
        print(f"✅ {model.name}")
        if hasattr(model, 'display_name'):
            print(f"   Display name: {model.display_name}")
        if hasattr(model, 'description'):
            print(f"   Description: {model.description[:100]}...")
        print()
    
    print("="*70)
    print("You can use any of the model names listed above in your chatbot!")
    print("="*70)
    
except Exception as e:
    print(f"❌ Error listing models: {str(e)}")
    print()
    print("This might mean:")
    print("1. Your API key doesn't have permission to list models")
    print("2. You need to create a NEW API key from aistudio.google.com/apikey")
