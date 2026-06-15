#!/usr/bin/env python3
"""
Test script for Ollama connection
Run this to verify Ollama is properly installed and configured
"""

import asyncio
import sys
from infrastructure.ai.ollama_client import OllamaClient
from infrastructure.logging import get_logger

logger = get_logger(__name__)


async def test_ollama():
    """Test Ollama connection and basic functionality"""
    
    print("\n" + "=" * 60)
    print("🤖 OLLAMA CONNECTION TEST")
    print("=" * 60 + "\n")
    
    # Configuration
    base_url = "http://127.0.0.1:11434"
    model = "mistral"
    
    print(f"Testing connection to: {base_url}")
    print(f"Using model: {model}\n")
    
    # Create client
    client = OllamaClient(base_url=base_url, model=model)
    
    try:
        # Test connection
        print("1️⃣  Testing connection...")
        connection_ok = await client.check_connection()
        
        if not connection_ok:
            print("❌ Could not connect to Ollama!")
            print("\nTo install Ollama:")
            print("  1. Download: https://ollama.ai")
            print("  2. Install and run: ollama serve")
            print("  3. Download model: ollama pull mistral")
            return False
        
        print("✅ Connected successfully!\n")
        
        # Test simple generation
        print("2️⃣  Testing generation...")
        response = await client.generate(
            prompt="Say hello in one word",
            temperature=0.1,
            timeout=15
        )
        
        if response:
            print(f"✅ Generated response: {response[:100]}\n")
        else:
            print("❌ Failed to generate response\n")
            return False
        
        # Test classification
        print("3️⃣  Testing classification...")
        result = await client.classify(
            text="Check out this amazing deal! Click here for free money!!!",
            classification_type="spam"
        )
        
        if result:
            print(f"✅ Classification result:")
            print(f"   Type: {result.get('type')}")
            print(f"   Confidence: {result.get('confidence'):.2f}")
            print(f"   Reason: {result.get('reason')}\n")
        else:
            print("❌ Failed to classify\n")
            return False
        
        print("=" * 60)
        print("✅ All tests passed! Ollama is ready to use.")
        print("=" * 60)
        print("\nYou can now:")
        print("  • Start the bot: python main.py")
        print("  • Use /ai_chat command in Discord")
        print("  • Use /ai_test to check status from bot\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await client.close_session()


if __name__ == "__main__":
    success = asyncio.run(test_ollama())
    sys.exit(0 if success else 1)
