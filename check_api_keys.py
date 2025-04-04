
import os
print("API Key Check:")
print(f"GOOGLE_API_KEY found: {'Yes' if os.getenv('GOOGLE_API_KEY') else 'No'}")
print(f"GOOGLE_CSE_ID found: {'Yes' if os.getenv('GOOGLE_CSE_ID') else 'No'}")
print(f"OPENAI_API_KEY found: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
