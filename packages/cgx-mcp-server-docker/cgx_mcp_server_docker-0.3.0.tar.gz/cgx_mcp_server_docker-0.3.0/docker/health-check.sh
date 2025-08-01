#!/bin/bash
set -euo pipefail

# MCP Docker Server Health Check
# This script verifies both SSH connection and MCP server health

# Configuration
SSH_ALIAS="xmind-vm"
MCP_PORT="8080"
CONNECTION_TIMEOUT=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "[INFO] $1" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Check SSH Docker connection (if using SSH transport)
check_ssh_docker() {
    if [ -n "${DOCKER_HOST:-}" ] && [[ "$DOCKER_HOST" == ssh://* ]]; then
        log_info "Checking SSH Docker connection..."
        
        if ssh -o ConnectTimeout=${CONNECTION_TIMEOUT} -o BatchMode=yes "${SSH_ALIAS}" "docker ps > /dev/null 2>&1"; then
            log_success "SSH Docker connection healthy"
            return 0
        else
            log_error "SSH Docker connection failed"
            return 1
        fi
    else
        log_info "Not using SSH Docker transport, skipping SSH check"
        return 0
    fi
}

# Check MCP server HTTP endpoint
check_mcp_server() {
    log_info "Checking MCP server HTTP endpoint..."
    
    if curl -f -s --max-time ${CONNECTION_TIMEOUT} "http://localhost:${MCP_PORT}/" >/dev/null 2>&1; then
        log_success "MCP server HTTP endpoint healthy"
        return 0
    else
        log_warning "MCP server HTTP endpoint not responding"
        
        # Fallback: check if the process is running
        if pgrep -f "mcp-server-docker" >/dev/null; then
            log_info "MCP server process is running"
            return 0
        else
            log_error "MCP server process not found"
            return 1
        fi
    fi
}

# Main health check
main() {
    log_info "Starting health check..."
    
    local exit_code=0
    
    # Check SSH Docker connection
    if ! check_ssh_docker; then
        exit_code=1
    fi
    
    # Check MCP server
    if ! check_mcp_server; then
        exit_code=1
    fi
    
    if [ $exit_code -eq 0 ]; then
        log_success "All health checks passed"
    else
        log_error "Health check failed"
    fi
    
    exit $exit_code
}

# Run main function
main "$@"
