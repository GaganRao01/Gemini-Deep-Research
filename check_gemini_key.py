import os
import sys
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    print("Error: google-generativeai package not installed.")
    print("Install it with: pip install google-generativeai")
    sys.exit(1)

def check_gemini_key():
    # Load environment variables
    load_dotenv()
    
    # Get the Google API key
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables or .env file.")
        print("Please add your Google API key to the .env file or environment variables:")
        print("GOOGLE_API_KEY=your_google_api_key_here")
        return False
    
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Get available models
        models = genai.list_models()
        
        # Filter for Gemini models
        gemini_models = [model for model in models if "gemini" in model.name]
        
        if not gemini_models:
            print("❌ No Gemini models available with your API key.")
            return False
            
        print("✅ GOOGLE_API_KEY is valid and has access to these Gemini models:")
        for model in gemini_models:
            print(f"  - {model.name}")
            
        # Try a simple generation with gemini-1.5-pro
        gemini_pro = next((m for m in gemini_models if "gemini-1.5-pro" in m.name), None)
        
        if gemini_pro:
            print("\nTesting API with a simple prompt...")
            
            model = genai.GenerativeModel(gemini_pro.name)
            response = model.generate_content("Hello, what are you capable of?")
            
            print("\nResponse from Gemini:")
            print("-" * 50)
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
            print("-" * 50)
            
            print("\n✅ Successfully connected to Gemini API and generated content!")
            return True
        else:
            print("\n⚠️ gemini-1.5-pro model not available. Please check your API access.")
            if gemini_models:
                print("You can still use the available models in your code.")
                return True
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Gemini API: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("CHECKING GOOGLE GEMINI API ACCESS")
    print("=" * 50)
    
    success = check_gemini_key()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Gemini API check completed successfully!")
        print("You can now use the research_crew_deepresearch.py script with Gemini.")
    else:
        print("❌ Gemini API check failed.")
        print("Please check your API key and make sure you have access to Gemini models.")
    print("=" * 50) 