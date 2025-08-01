#!/usr/bin/env python3
"""
Startup script for MCP Docker Server
Supports both stdio and streamable-http transports
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server_docker import main

if __name__ == "__main__":
    sys.exit(main())
