"""
test_api.py - Test if your Google AI API keys are working
Uses the NEW google-genai package (not the deprecated google-generativeai)
Run this from your project folder: python test_api.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

print("="*70)
print("GOOGLE AI API KEY TEST - Using NEW google-genai Package")
print("="*70)
print()

# Load .env file
config_dir = Path(__file__).parent / 'config'
env_path = config_dir / '.env'

print(f"Loading .env from: {env_path}")
load_dotenv(env_path)
print()

# Test each API key
for i in range(1, 10):  # Check up to 9 keys
    key = os.getenv(f'GOOGLE_API_KEY_{i}')
    
    if not key:
        if i == 1:
            print("❌ ERROR: No API keys found in .env file!")
            print("Please check your config/.env file")
        break
    
    print(f"Testing API Key #{i}")
    print(f"Key starts with: {key[:20]}...")
    
    try:
        # Create client with this key (NEW syntax)
        client = genai.Client(api_key=key)
        
        # Try to generate content using NEW API
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents='Say "API test successful" and nothing else',
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=100,
            )
        )
        
        print(f"✅ SUCCESS! Key #{i} is working!")
        print(f"Response: {response.text}")
        print()
        
    except Exception as e:
        print(f"❌ FAILED! Key #{i} has an error")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print()
        
        # Give specific advice based on error
        error_msg = str(e).lower()
        if "api key not valid" in error_msg or "invalid" in error_msg:
            print("💡 This key appears to be invalid. Check:")
            print("   - Did you copy the full key from Google AI Studio?")
            print("   - Are there any extra spaces in your .env file?")
        elif "404" in error_msg or "not found" in error_msg:
            print("💡 The model might not be available with this key.")
            print("   - Try creating a new API key at aistudio.google.com")
        elif "quota" in error_msg or "429" in error_msg:
            print("💡 This key has hit its quota limit.")
            print("   - Wait for quota reset or use a different key")
        print()

print("="*70)
print("TEST COMPLETE")
print("="*70)
print()
print("If all keys failed:")
print("1. Go to https://aistudio.google.com/apikey")
print("2. Create NEW API keys")
print("3. Copy them carefully into config/.env")
print("4. Make sure format is: GOOGLE_API_KEY_1=AIzaSy...")
print("   (No spaces, no quotes)")
