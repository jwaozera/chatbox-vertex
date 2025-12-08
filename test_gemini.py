import google.generativeai as genai
import os

key = '' # Key provided by user
genai.configure(api_key=key)

try:
    print("Listing models...")
    for m in genai.list_models():
        print(f"Found: {m.name}")
        if 'generateContent' in m.supported_generation_methods:
            print(f"  - Supports generateContent")
except Exception as e:
    print(f"Error: {e}")
