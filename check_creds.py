import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables from .env file
print("Loading environment variables from .env file...")
load_dotenv()

# Print environment variables
print("Environment Variables:")
print(f"GOOGLE_API_KEY configured: {bool(os.getenv('GOOGLE_API_KEY'))}")
print(f"GOOGLE_CSE_ID configured: {bool(os.getenv('GOOGLE_CSE_ID'))}")
print(f"OPENAI_API_KEY configured: {bool(os.getenv('OPENAI_API_KEY'))}")

# Get API credentials
api_key = os.getenv("GOOGLE_API_KEY")
cse_id = os.getenv("GOOGLE_CSE_ID")

if not api_key:
    print("\nError: GOOGLE_API_KEY environment variable is not set")
    print("Please create a .env file with your API keys (see .env.example)")
    exit(1)
    
if not cse_id:
    print("\nError: GOOGLE_CSE_ID environment variable is not set")
    print("Please create a .env file with your API keys (see .env.example)")
    exit(1)

print("\nAttempting Google search with the following parameters:")
query = "AI in healthcare"
num_results = 3
print(f"- Query: {query}")
print(f"- Num Results: {num_results}")
print(f"- API Key (first 5 chars): {api_key[:5]}...")
print(f"- CSE ID (first 5 chars): {cse_id[:5]}...")

try:
    # Build the service
    service = build("customsearch", "v1", developerKey=api_key)
    
    # Prepare search parameters
    search_params = {
        'q': query,
        'cx': cse_id,
        'num': min(num_results, 10)  # API limits to 10 results max per call
    }
    
    # Execute the search
    print("\nExecuting search...")
    result = service.cse().list(**search_params).execute()
    
    # Process results
    items = result.get('items', [])
    
    if not items:
        print("No search results found.")
    else:
        print(f"\nFound {len(items)} results:")
        for i, item in enumerate(items, 1):
            print(f"\nResult {i}:")
            print(f"- Title: {item.get('title', 'No title')}")
            print(f"- Link: {item.get('link', 'No link')}")
            print(f"- Snippet: {item.get('snippet', 'No snippet')[:100]}...")
            
except HttpError as e:
    print(f"\nGoogle API HTTP error: {e}")
except Exception as e:
    print(f"\nUnexpected error: {e}") 