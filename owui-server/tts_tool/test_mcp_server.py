#!/usr/bin/env python3
"""
Test script for the TTS MCP server
"""

import os
import sys
import json

# Set environment variables
os.environ["TTS_API_TOKEN"] = "test_token"
os.environ["TTS_API_URL"] = "https://tts.cyborg.fi/tickets/api/v1/"

# Import the MCP server
import tts_mcp_server

def test_health_check():
    """Test the health check function"""
    print("Testing health_check...")
    try:
        # Access the underlying function from the MCP tool
        result = tts_mcp_server.tts_client.health_check()
        print(f"Health check result: {result}")
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_list_tickets():
    """Test the list_tickets function"""
    print("Testing list_tickets...")
    try:
        # Access the underlying function from the MCP tool
        result = tts_mcp_server.tts_client.list_tickets({"limit": 5})
        print(f"List tickets result: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        print(f"List tickets failed: {e}")
        return False

def test_list_users():
    """Test the list_users function"""
    print("Testing list_users...")
    try:
        # Access the underlying function from the MCP tool
        result = tts_mcp_server.tts_client.list_users(limit=5)
        print(f"List users result: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        print(f"List users failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Testing TTS MCP Server")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_list_tickets,
        test_list_users
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"\n{'-' * 30}")
        try:
            if test():
                print("✅ PASSED")
                passed += 1
            else:
                print("❌ FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ FAILED with exception: {e}")
            failed += 1
    
    print(f"\n{'=' * 50}")
    print(f"Test Results: {passed} passed, {failed} failed")
    print(f"{'=' * 50}")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)