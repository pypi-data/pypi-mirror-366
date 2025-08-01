#!/usr/bin/env python3
"""
Simple test to verify the list_images tool works correctly
"""

import asyncio
import docker
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server_docker.server import app
from mcp_server_docker.settings import ServerSettings
import mcp_server_docker.server as server_module

async def test_list_images():
    """Test the list_images tool directly"""
    try:
        # Initialize Docker client and settings
        docker_client = docker.from_env()
        settings = ServerSettings()
        
        # Set global variables in server module
        server_module._docker = docker_client
        server_module._server_settings = settings
        
        print("Testing list_images tool...")
        
        # Test the list_images tool directly
        result = await app.call_tool('list_images', {})
        
        print("✅ list_images tool executed successfully!")
        print("Result:")
        for content in result:
            # Parse and pretty print the JSON
            data = json.loads(content.text)
            print(json.dumps(data, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ list_images tool failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_list_containers():
    """Test the list_containers tool"""
    try:
        print("\nTesting list_containers tool...")
        result = await app.call_tool('list_containers', {'all': True})
        
        print("✅ list_containers tool executed successfully!")
        print("Result:")
        for content in result:
            data = json.loads(content.text)
            print(json.dumps(data, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ list_containers tool failed: {e}")
        return False

async def main():
    """Run basic tool tests"""
    print("🧪 Testing MCP Docker Server tools...")
    
    # Test Docker connection first
    try:
        docker_client = docker.from_env()
        docker_client.ping()
        print("✅ Docker connection successful")
    except Exception as e:
        print(f"❌ Docker connection failed: {e}")
        return 1
    
    # Test tools
    tests = [
        test_list_images(),
        test_list_containers(),
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    success_count = sum(1 for r in results if r is True)
    total_tests = len(tests)
    
    print(f"\n📊 Test Results: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! The server is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
