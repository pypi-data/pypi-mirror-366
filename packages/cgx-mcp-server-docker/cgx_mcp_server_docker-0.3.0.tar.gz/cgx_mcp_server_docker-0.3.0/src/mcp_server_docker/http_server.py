import asyncio  
import contextlib
import logging
from typing import AsyncIterator
import docker  
import uvicorn
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse

from .settings import ServerSettings  

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint for the MCP server."""
    return JSONResponse({"status": "healthy", "service": "mcp-docker-server"})

async def run_http(settings: ServerSettings, docker_client: docker.DockerClient, host: str = "0.0.0.0", port: int = 8080):  
    """Run the server over HTTP using streamable HTTP transport."""  
    # Import and configure the existing server
    from . import server
    
    # Set the global variables  
    server._docker = docker_client
    server._server_settings = settings
    
    logger.info(f"Starting MCP Docker Server with streamable HTTP on http://{host}:{port}")
    logger.info("Server will be available at all endpoints")
    logger.info("Use Ctrl+C to stop the server.")
    
    try:
        # Create streamable HTTP session manager with the MCP server
        session_manager = StreamableHTTPSessionManager(server.app)
        
        # Create Starlette app with health check
        routes = [
            Route("/health", health_check, methods=["GET"]),
        ]
        
        starlette_app = Starlette(routes=routes)
        
        # Create combined ASGI application
        async def combined_app(scope, receive, send):
            # Handle health check and other routes first
            if scope["type"] == "http" and scope["path"] == "/health":
                await starlette_app(scope, receive, send)
                return
            
            # Handle MCP requests
            try:
                await session_manager.handle_request(scope, receive, send)
            except Exception as e:
                logger.error(f"Error handling MCP request: {e}")
                # Send error response
                response = {
                    "status": 500,
                    "body": b'{"error": "Internal server error"}',
                    "headers": [(b"content-type", b"application/json")]
                }
                await send(response)
        
        # Configure and run the uvicorn server  
        config = uvicorn.Config(  
            app=combined_app,  
            host=host,  
            port=port,  
            log_level="info",
            access_log=True
        )  
        uvicorn_server = uvicorn.Server(config)  
        
        # Run the session manager and uvicorn server together
        async with session_manager.run():
            await uvicorn_server.serve()
            
    except Exception as e:
        logger.error(f"Failed to start HTTP server: {e}")
        raise