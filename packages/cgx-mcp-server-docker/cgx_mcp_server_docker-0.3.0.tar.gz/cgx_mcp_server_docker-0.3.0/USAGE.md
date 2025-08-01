# MCP Docker Server Configuration Examples

## Using with different transports

### 1. Standard I/O (default)
```bash
python run_server.py
# or
python -m mcp_server_docker --transport stdio
```

### 2. Streamable HTTP 
```bash
python run_server.py --transport streamable-http --host 0.0.0.0 --port 8080
# or
python -m mcp_server_docker --transport streamable-http --host 0.0.0.0 --port 8080
```

### 3. HTTP (alias for streamable-http)
```bash
python run_server.py --transport http --host 0.0.0.0 --port 8080
```

## Installing Dependencies

```bash
pip install -e .
# or for development
pip install -e ".[dev]"
```

## Testing the Server

### Test HTTP Transport
```bash
# Start the server
python run_server.py --transport streamable-http --port 8080

# Test health check in another terminal
curl http://localhost:8080/health
```

### Test with Agno App
Make sure to use the correct transport when configuring the MCP server in your Agno app.

For HTTP transport, use:
- URL: `http://localhost:8080`
- Transport: `streamable-http`

For stdio transport, use the direct command:
- Command: `python /path/to/run_server.py --transport stdio`

## Troubleshooting

1. **ClosedResourceError**: Usually indicates improper session management. This has been fixed in the latest version.

2. **Docker Connection Issues**: Make sure Docker is running and accessible:
   ```bash
   docker info
   ```

3. **Import Errors**: Install all dependencies:
   ```bash
   pip install docker mcp paramiko pydantic-settings uvicorn starlette
   ```

4. **Port Already in Use**: Change the port:
   ```bash
   python run_server.py --transport streamable-http --port 8081
   ```
