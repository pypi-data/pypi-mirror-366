#!/usr/bin/env python3
"""
Test script for MCP Docker Server
Tests both stdio and HTTP transports
"""

import asyncio
import json
import subprocess
import sys
import time
import requests
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

async def test_stdio_transport():
    """Test the stdio transport"""
    print("Testing stdio transport...")
    
    try:
        # Start the server process
        process = subprocess.Popen(
            [sys.executable, "run_server.py", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Create MCP client
        session_manager = stdio_client(process.stdin, process.stdout)
        
        async with session_manager as session:
            # Initialize the session
            await session.initialize()
            
            # Test list_images tool
            print("Testing list_images tool...")
            result = await session.call_tool("list_images", {})
            print(f"list_images result: {json.dumps(result.content, indent=2)}")
            
            # Test list_containers tool
            print("Testing list_containers tool...")
            result = await session.call_tool("list_containers", {"all": True})
            print(f"list_containers result: {json.dumps(result.content, indent=2)}")
            
        process.terminate()
        process.wait()
        print("stdio transport test completed successfully!")
        return True
        
    except Exception as e:
        print(f"stdio transport test failed: {e}")
        if 'process' in locals():
            process.terminate()
        return False

async def test_http_transport():
    """Test the HTTP transport"""
    print("Testing HTTP transport...")
    
    try:
        # Start the server process
        process = subprocess.Popen(
            [sys.executable, "run_server.py", "--transport", "streamable-http", "--port", "8081"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        print("Waiting for server to start...")
        time.sleep(3)
        
        # Test health endpoint
        response = requests.get("http://localhost:8081/health")
        print(f"Health check status: {response.status_code}")
        print(f"Health check response: {response.json()}")
        
        # For HTTP transport, we would need to implement a proper MCP HTTP client
        # For now, just verify the server is running
        
        process.terminate()
        process.wait()
        print("HTTP transport test completed successfully!")
        return True
        
    except Exception as e:
        print(f"HTTP transport test failed: {e}")
        if 'process' in locals():
            process.terminate()
        return False

async def main():
    """Run all tests"""
    print("Starting MCP Docker Server tests...")
    
    # Test stdio transport
    stdio_success = await test_stdio_transport()
    
    # Test HTTP transport
    http_success = await test_http_transport()
    
    if stdio_success and http_success:
        print("\nAll tests passed! ✅")
        return 0
    else:
        print("\nSome tests failed! ❌")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
