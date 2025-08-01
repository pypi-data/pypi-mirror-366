import asyncio  
import argparse  
import logging
import docker  
from .settings import ServerSettings  
from .server import run_stdio  
from .http_server import run_http  

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
  
def main():  
    """Main entry point supporting both stdio and streamable-http transports."""  
    parser = argparse.ArgumentParser(description="MCP Docker Server")  
    parser.add_argument(  
        "--transport",   
        choices=["stdio", "streamable-http", "http"],   
        default="stdio",  
        help="Transport method (default: stdio). Use 'streamable-http' for HTTP with streaming support."  
    )  
    parser.add_argument(  
        "--host",   
        default="0.0.0.0",  
        help="Host to bind HTTP server (default: 0.0.0.0)"  
    )  
    parser.add_argument(  
        "--port",   
        type=int,   
        default=8080,  
        help="Port for HTTP server (default: 8080)"  
    )  
      
    args = parser.parse_args()  
      
    # Initialize settings and Docker client  
    try:
        settings = ServerSettings()  
        docker_client = docker.from_env()
        
        # Test Docker connection
        logger.info("Testing Docker connection...")
        docker_client.ping()
        logger.info("Docker connection successful")
        
    except Exception as e:
        logger.error(f"Failed to initialize Docker client: {e}")
        logger.error("Please ensure Docker is running and accessible")
        return 1
      
    # Run appropriate transport  
    try:
        if args.transport in ["http", "streamable-http"]:  
            logger.info(f"Starting server with {args.transport} transport")
            asyncio.run(run_http(settings, docker_client, args.host, args.port))  
        else:  
            logger.info("Starting server with stdio transport")
            asyncio.run(run_stdio(settings, docker_client))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}")
        return 1
  
if __name__ == "__main__":  
    exit(main())

# Optionally expose other important items at package level
__all__ = ["main", "run_stdio", "run_http", "ServerSettings"]

