#!/usr/bin/env python3
"""Verify OpenAI API key is correctly configured and working"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from openai import OpenAI
import os

# Load environment variables from .env file
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

def verify_api_key():
    """Verify OpenAI API key is set and working"""
    print("="*70)
    print("OpenAI API Key Verification")
    print("="*70)
    
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ OPENAI_API_KEY not found in environment variables")
        print("   Please check your .env file at the project root")
        return False
    
    # Mask the key for display (show first 10 and last 4 characters)
    masked_key = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
    print(f"\n✓ OPENAI_API_KEY found: {masked_key}")
    
    # Test the API key by making a simple request
    print("\n" + "-"*70)
    print("Testing API key with a simple request...")
    print("-"*70)
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Make a simple, low-cost API call to verify the key works
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'API key is working' if you can read this."}
            ],
            max_tokens=10,
            temperature=0
        )
        
        result = response.choices[0].message.content.strip()
        print(f"\n✓ API response received: {result}")
        print("\n✅ API KEY VERIFICATION SUCCESSFUL")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"\n❌ API key verification failed: {e}")
        print("\nThis could mean:")
        print("  • The API key is invalid or expired")
        print("  • There's a network connectivity issue")
        print("  • The OpenAI API service is unavailable")
        print("="*70)
        return False


if __name__ == "__main__":
    success = verify_api_key()
    sys.exit(0 if success else 1)




