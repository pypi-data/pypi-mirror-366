# Multi-stage Dockerfile for MCP Docker Server

# Stage 1: Development build from source
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy dependency files
COPY uv.lock pyproject.toml /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Copy source code
COPY ./src /app/src
COPY README.md LICENSE /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Stage 2: Final runtime image
FROM python:3.12-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Install system dependencies including Docker CLI
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN groupadd -r mcpuser && useradd -r -g mcpuser -s /bin/bash mcpuser

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder --chown=mcpuser:mcpuser /app/.venv /app/.venv

# Create configuration and data directories
RUN mkdir -p /app/config /app/data && chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Expose the default HTTP port
EXPOSE 8080

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Default command - run in HTTP mode
ENTRYPOINT ["mcp-server-docker"]
CMD ["--transport", "http", "--host", "0.0.0.0", "--port", "8080"]
