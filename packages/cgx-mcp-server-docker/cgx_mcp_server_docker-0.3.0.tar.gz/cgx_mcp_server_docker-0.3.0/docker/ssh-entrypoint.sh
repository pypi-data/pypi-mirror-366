#!/bin/bash
set -euo pipefail

# MCP Docker Server SSH Entrypoint
# This script sets up SSH connection to remote Docker daemon and starts the MCP server

# Configuration
SSH_HOST="193.248.63.231"
SSH_PORT="1555"
SSH_USER="xmind"
SSH_KEY_NAME="xmind_infraops"
SSH_ALIAS="xmind-vm"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Setup SSH directory and permissions
setup_ssh_directory() {
    log_info "Setting up SSH directory..."
    mkdir -p /root/.ssh
    chmod 700 /root/.ssh
}

# Setup SSH private key from file or environment variable
setup_ssh_key() {
    log_info "Setting up SSH private key..."
    
    if [ -f "/app/${SSH_KEY_NAME}" ]; then
        log_info "Using SSH private key from mounted file"
        cp "/app/${SSH_KEY_NAME}" "/root/.ssh/${SSH_KEY_NAME}"
        chmod 600 "/root/.ssh/${SSH_KEY_NAME}"
        log_success "SSH private key set up successfully from file"
        
        # Verify key file permissions
        ls -la "/root/.ssh/${SSH_KEY_NAME}"
        
        # Validate the key format
        if ssh-keygen -l -f "/root/.ssh/${SSH_KEY_NAME}" >/dev/null 2>&1; then
            log_success "SSH key validation successful"
        else
            log_warning "SSH key validation failed - key might be malformed"
        fi
        
    elif [ -n "${MCP_DOCKER_SSH_PRIVATE_KEY:-}" ]; then
        log_info "Using SSH private key from environment variable"
        printf '%s\n' "$MCP_DOCKER_SSH_PRIVATE_KEY" > "/root/.ssh/${SSH_KEY_NAME}"
        chmod 600 "/root/.ssh/${SSH_KEY_NAME}"
        log_success "SSH private key set up successfully from environment variable"
        
        # Verify key file permissions
        ls -la "/root/.ssh/${SSH_KEY_NAME}"
        
        # Validate the key format
        if ssh-keygen -l -f "/root/.ssh/${SSH_KEY_NAME}" >/dev/null 2>&1; then
            log_success "SSH key validation successful"
        else
            log_warning "SSH key validation failed - key might be malformed"
        fi
        
    else
        log_error "Neither ${SSH_KEY_NAME} file nor MCP_DOCKER_SSH_PRIVATE_KEY environment variable found!"
        log_error "Please provide the SSH private key either as a file or environment variable."
        exit 1
    fi
}

# Setup SSH agent and add key
setup_ssh_agent() {
    log_info "Starting SSH agent..."
    eval $(ssh-agent -s)
    
    log_info "Adding SSH key to agent..."
    ssh-add "/root/.ssh/${SSH_KEY_NAME}"
    
    log_info "Keys loaded in SSH agent:"
    ssh-add -l
}

# Setup SSH known hosts and config
setup_ssh_config() {
    log_info "Setting up SSH configuration..."
    
    # Add remote host to known_hosts
    ssh-keyscan -p "${SSH_PORT}" -H "${SSH_HOST}" >> /root/.ssh/known_hosts 2>/dev/null
    
    # Create SSH config
    cat > /root/.ssh/config << EOF
Host ${SSH_ALIAS}
    HostName ${SSH_HOST}
    User ${SSH_USER}
    Port ${SSH_PORT}
    IdentityFile /root/.ssh/${SSH_KEY_NAME}
    IdentitiesOnly yes
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel ERROR
    BatchMode yes
    PasswordAuthentication no
    PubkeyAuthentication yes
    PreferredAuthentications publickey
EOF
    
    chmod 600 /root/.ssh/config
    log_success "SSH configuration created"
}

# Test SSH connection
test_ssh_connection() {
    log_info "Testing SSH connection..."
    
    if ssh -o ConnectTimeout=10 -o BatchMode=yes "${SSH_ALIAS}" echo "SSH connection successful"; then
        log_success "SSH connection test passed"
    else
        log_error "SSH connection failed!"
        log_info "Debugging SSH configuration:"
        echo "SSH config file:"
        cat /root/.ssh/config
        echo "SSH private key file permissions:"
        ls -la "/root/.ssh/${SSH_KEY_NAME}"
        echo "SSH agent keys:"
        ssh-add -l
        echo "Testing SSH with verbose output:"
        ssh -vvv -o ConnectTimeout=10 -o BatchMode=yes "${SSH_ALIAS}" echo "SSH connection test" 2>&1 | head -20
        exit 1
    fi
}

# Setup Docker environment
setup_docker_environment() {
    log_info "Setting up Docker environment..."
    
    # Set DOCKER_HOST if not already set
    if [ -z "${DOCKER_HOST:-}" ]; then
        export DOCKER_HOST="ssh://${SSH_USER}@${SSH_HOST}:${SSH_PORT}"
        log_success "DOCKER_HOST set to: $DOCKER_HOST"
    fi
    
    # Export SSH_AUTH_SOCK so the MCP server can use the SSH agent
    export SSH_AUTH_SOCK="$SSH_AUTH_SOCK"
    log_info "SSH_AUTH_SOCK exported: $SSH_AUTH_SOCK"
    
    # Set additional SSH environment variables to ensure proper authentication
    export DOCKER_SSH_COMMAND="ssh -i /root/.ssh/${SSH_KEY_NAME} -o StrictHostKeyChecking=no"
    
    # Create SSH wrapper
    cat > /usr/local/bin/docker-ssh << EOF
#!/bin/bash
exec ssh -F /root/.ssh/config "\$@"
EOF
    chmod +x /usr/local/bin/docker-ssh
    
    # Set Docker to use our SSH wrapper
    export DOCKER_SSH_COMMAND="/usr/local/bin/docker-ssh"
    log_success "Docker SSH environment configured"
}

# Run debug checks if enabled
run_debug_checks() {
    if [ "${DEBUG:-0}" = "1" ]; then
        log_info "Running SSH debug checks..."
        echo "=== SSH Configuration Debug ==="
        echo "SSH config:"
        cat /root/.ssh/config
        echo "SSH key file:"
        ls -la "/root/.ssh/${SSH_KEY_NAME}"
        echo "SSH agent keys:"
        ssh-add -l
        echo "Testing Docker over SSH:"
        ssh "${SSH_ALIAS}" "docker version" || echo "Docker command failed over SSH"
        echo "Testing SSH wrapper:"
        /usr/local/bin/docker-ssh "${SSH_ALIAS}" "echo 'SSH wrapper test successful'" || echo "SSH wrapper failed"
        echo "Environment variables:"
        echo "DOCKER_HOST=$DOCKER_HOST"
        echo "SSH_AUTH_SOCK=$SSH_AUTH_SOCK"
        echo "DOCKER_SSH_COMMAND=$DOCKER_SSH_COMMAND"
        echo "=== End SSH Debug ==="
    fi
}

# Main execution
main() {
    log_info "Starting MCP Docker Server SSH setup..."
    
    # Setup SSH
    setup_ssh_directory
    setup_ssh_key
    setup_ssh_agent
    setup_ssh_config
    test_ssh_connection
    
    # Setup Docker
    setup_docker_environment
    
    # Debug if enabled
    run_debug_checks
    
    log_success "SSH setup completed successfully"
    log_info "Starting MCP server with DOCKER_HOST: ${DOCKER_HOST}"
    
    # Show startup information
    log_info "About to start main application: $*"
    log_info "Current working directory: $(pwd)"
    log_info "Available files:"
    ls -la
    
    # Execute the original command
    exec "$@"
}

# Run main function with all arguments
main "$@"
