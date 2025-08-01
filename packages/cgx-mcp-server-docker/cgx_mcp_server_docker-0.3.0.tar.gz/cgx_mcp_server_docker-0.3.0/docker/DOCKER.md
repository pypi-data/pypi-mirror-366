# Docker Deployment Guide for MCP Docker Server

This guide shows you how to run the MCP Docker Server using Docker containers.

## 🐳 Quick Start

### Option 1: Using PyPI Version (Recommended for Production)

Build and run using the pre-built package from PyPI:

```bash
# Build the image
docker build -f Dockerfile.pypi -t mcp-docker-server:latest .

# Run the container
docker run -d \
  --name mcp-docker-server \
  -p 8080:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  mcp-docker-server:latest
```

### Option 2: Using Docker Compose (Easiest)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 3: Building from Source

```bash
# Build from source
docker build -t mcp-docker-server:dev .

# Run the container
docker run -d \
  --name mcp-docker-server \
  -p 8080:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  mcp-docker-server:dev
```

## 🔧 Configuration

### Environment Variables

- `PYTHONUNBUFFERED=1` - Enable unbuffered Python output
- `PYTHONDONTWRITEBYTECODE=1` - Prevent Python from writing .pyc files

### Volumes

- `/var/run/docker.sock:/var/run/docker.sock` - **Required**: Docker socket for container management
- `./config:/app/config` - Optional: Configuration files
- `./data:/app/data` - Optional: Data persistence

### Ports

- `8080` - HTTP server port (default)

## 🚀 Usage Examples

### Basic HTTP Server

```bash
docker run -d \
  --name mcp-docker-server \
  -p 8080:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  mcp-docker-server:latest
```

### Custom Port

```bash
docker run -d \
  --name mcp-docker-server \
  -p 9090:9090 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  mcp-docker-server:latest \
  --transport http --host 0.0.0.0 --port 9090
```

### STDIO Mode (for MCP clients)

```bash
docker run -it \
  --name mcp-docker-server \
  -v /var/run/docker.sock:/var/run/docker.sock \
  mcp-docker-server:latest \
  --transport stdio
```

## 🔍 Health Checks

The container includes a health check that verifies the HTTP server is responding:

```bash
# Check container health
docker ps

# View health check logs
docker inspect mcp-docker-server --format='{{.State.Health.Status}}'
```

## 📊 Monitoring

### View Logs

```bash
# Follow logs
docker logs -f mcp-docker-server

# With docker-compose
docker-compose logs -f mcp-docker-server
```

### Connect to Container

```bash
# Get a shell in the running container
docker exec -it mcp-docker-server /bin/bash
```

## 🔐 Security Considerations

- The container runs as a non-root user (`mcpuser`) for security
- Docker socket is mounted read-only when possible
- Only necessary system packages are installed
- Use specific version tags in production

## 🛠 Development

### Building Different Versions

```bash
# Build latest development version
docker build -t mcp-docker-server:dev .

# Build specific PyPI version
docker build -f Dockerfile.pypi --build-arg VERSION=0.2.2 -t mcp-docker-server:0.2.2 .
```

### Custom Configuration

Create a `config` directory with your settings:

```bash
mkdir -p config data
echo '{"setting": "value"}' > config/settings.json

docker run -d \
  --name mcp-docker-server \
  -p 8080:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  mcp-docker-server:latest
```

## 🔗 Integration

### With MCP Inspector

Once the container is running, you can connect with MCP Inspector:

```json
{
  "transport": "http",
  "url": "http://localhost:8080"
}
```

### With Other Applications

The server exposes a standard MCP-over-HTTP interface at `http://localhost:8080`

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs mcp-docker-server

# Check if Docker socket is accessible
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock docker:latest docker ps
```

### Permission Issues

```bash
# Ensure Docker socket has correct permissions
sudo chmod 666 /var/run/docker.sock

# Or add your user to docker group
sudo usermod -aG docker $USER
```

### Port Already in Use

```bash
# Find what's using the port
sudo netstat -tulpn | grep :8080

# Use a different port
docker run -p 8081:8080 mcp-docker-server:latest
```
