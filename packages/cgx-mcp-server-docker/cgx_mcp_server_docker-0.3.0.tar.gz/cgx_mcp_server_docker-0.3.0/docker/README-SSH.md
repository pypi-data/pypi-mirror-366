# MCP Docker Server with SSH Remote Docker Access

This setup allows the MCP Docker server to connect to a remote Docker daemon via SSH, enabling Docker management on remote hosts.

## Features

- ✅ SSH connection to remote Docker daemon
- ✅ Secure key-based authentication
- ✅ Health monitoring with automatic restart
- ✅ Debug mode for troubleshooting
- ✅ Flexible configuration options
- ✅ Clean, maintainable codebase

## Quick Start

### 1. Prepare SSH Key

Place your SSH private key as `xmind_infraops` in the project directory:

```bash
# Copy your SSH key to the project directory
cp /path/to/your/private/key ./xmind_infraops
chmod 600 ./xmind_infraops
```

### 2. Start the Container

```bash
# Build and start the container
docker-compose -f docker-compose.ssh.yml up -d --build

# Check container status
docker ps

# View logs
docker logs mcp-docker-server-ssh
```

### 3. Test the Connection

```bash
# Test MCP server connectivity
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"ping","id":1}'

# Run the connectivity test script
python test-mcp-connection.py
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `0` | Set to `1` to enable SSH debugging |
| `SSH_HOST` | `193.248.63.231` | Remote SSH host |
| `SSH_PORT` | `1555` | SSH port |
| `SSH_USER` | `xmind` | SSH username |
| `SSH_KEY_NAME` | `xmind_infraops` | SSH private key filename |
| `MCP_PORT` | `8080` | MCP server port |

### SSH Key Options

**Option 1: File Mount (Recommended)**
```yaml
volumes:
  - ./xmind_infraops:/app/xmind_infraops:ro
```

**Option 2: Environment Variable**
```yaml
environment:
  - MCP_DOCKER_SSH_PRIVATE_KEY=|
    -----BEGIN OPENSSH PRIVATE KEY-----
    your_private_key_content_here
    -----END OPENSSH PRIVATE KEY-----
```

## Architecture

```
┌─────────────────┐    SSH Tunnel    ┌─────────────────┐
│                 │◄─────────────────►│                 │
│   MCP Server    │    Port 1555     │  Remote Docker  │
│   (Container)   │                  │    Daemon       │
│                 │                  │                 │
└─────────────────┘                  └─────────────────┘
         ▲                                     
         │ HTTP/WebSocket                      
         │ Port 8080                           
         ▼                                     
┌─────────────────┐                           
│                 │                           
│  Client Apps    │                           
│  (Agno, etc.)   │                           
│                 │                           
└─────────────────┘                           
```

## Health Monitoring

The container includes comprehensive health checks:

- ✅ SSH connection to remote Docker daemon
- ✅ MCP server HTTP endpoint availability
- ✅ Process monitoring
- ✅ Automatic restart on failure

## Troubleshooting

### Enable Debug Mode

```bash
# Set DEBUG=1 in docker-compose.ssh.yml
docker-compose -f docker-compose.ssh.yml up -d --build

# View detailed logs
docker logs mcp-docker-server-ssh
```

### Common Issues

**SSH Connection Failed**
```bash
# Check SSH key permissions
ls -la ./xmind_infraops

# Test SSH manually
ssh -i ./xmind_infraops -p 1555 xmind@193.248.63.231

# Check container logs for SSH details
docker logs mcp-docker-server-ssh | grep SSH
```

**MCP Server Not Responding**
```bash
# Check if container is running
docker ps

# Check health status
docker inspect mcp-docker-server-ssh | grep Health -A 10

# Test endpoint manually
curl http://localhost:8080/
```

**Container Restart Loop**
```bash
# Check container logs
docker logs mcp-docker-server-ssh

# Run with debug mode
docker-compose -f docker-compose.ssh.yml down
# Edit docker-compose.ssh.yml: set DEBUG=1
docker-compose -f docker-compose.ssh.yml up --build
```

## File Structure

```
.
├── Dockerfile.ssh           # Main Dockerfile for SSH setup
├── docker-compose.ssh.yml   # Docker Compose configuration
├── ssh-entrypoint.sh        # SSH setup and entrypoint script
├── health-check.sh          # Health monitoring script
├── .env.example            # Environment variables template
├── test-mcp-connection.py  # Connection testing script
├── xmind_infraops          # SSH private key (not in git)
└── README-SSH.md           # This file
```

## Security Considerations

- 🔒 SSH keys are mounted read-only
- 🔒 Proper file permissions (600) enforced
- 🔒 SSH agent isolates key access
- 🔒 BatchMode prevents interactive prompts
- 🔒 StrictHostKeyChecking disabled for automation

## Integration with Agno

See `agno-mcp-fix.py` for proper Agno integration:

```python
from agno.tools.mcp import StreamableHTTPClientParams

server_params = StreamableHTTPClientParams(
    url="http://localhost:8080/mcp",
    timeout=timedelta(seconds=60),
    sse_read_timeout=timedelta(seconds=300)
)
```

## Maintenance

### Update MCP Server Version

```bash
# Edit Dockerfile.ssh, change:
RUN pip install cgx-mcp-server-docker==0.2.3  # New version

# Rebuild
docker-compose -f docker-compose.ssh.yml build --no-cache
docker-compose -f docker-compose.ssh.yml up -d
```

### Backup Configuration

```bash
# Backup SSH key and config
tar -czf mcp-ssh-backup.tar.gz xmind_infraops docker-compose.ssh.yml .env
```
