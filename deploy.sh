#!/bin/bash

# NVIDIA Control Panel API - Production Deployment Script
# This script handles the complete production deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="nvidia-control-panel-api"
APP_PORT=8000
ENV_FILE=".env"

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

# Check if running as root (for system-wide installation)
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. This will install system-wide."
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."

    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed."
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ "$(printf '%s\n' "$PYTHON_VERSION" "3.8" | sort -V | head -n1)" != "3.8" ]]; then
        log_error "Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
    log_success "Python $PYTHON_VERSION found"

    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is required but not installed."
        exit 1
    fi
    log_success "pip3 found"

    # Check if port is available
    if lsof -Pi :$APP_PORT -sTCP:LISTEN -t >/dev/null ; then
        log_warning "Port $APP_PORT is already in use"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Setup virtual environment
setup_venv() {
    log_info "Setting up Python virtual environment..."

    if [[ ! -d ".venv" ]]; then
        python3 -m venv .venv
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi

    # Activate virtual environment
    source .venv/bin/activate
    log_success "Virtual environment activated"

    # Upgrade pip
    pip install --upgrade pip
    log_success "pip upgraded"
}

# Install dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."

    source .venv/bin/activate

    # Install production dependencies
    pip install -r requirements.txt
    log_success "Dependencies installed"

    # Optional: Install monitoring dependencies
    if [[ -f "requirements-monitoring.txt" ]]; then
        pip install -r requirements-monitoring.txt
        log_success "Monitoring dependencies installed"
    fi
}

# Setup environment configuration
setup_environment() {
    log_info "Setting up environment configuration..."

    # Create .env file if it doesn't exist
    if [[ ! -f "$ENV_FILE" ]]; then
        cat > "$ENV_FILE" << EOF
# NVIDIA Control Panel API - Environment Configuration
# Copy this file and update values for your environment

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-change-this
DEBUG=False

# Server Configuration
HOST=0.0.0.0
PORT=$APP_PORT

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_TOKEN=your-production-api-token-change-this
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Monitoring Configuration
PROMETHEUS_PORT=9090
HEALTH_CHECK_INTERVAL=30
EOF
        log_success "Environment file created: $ENV_FILE"
        log_warning "Please update $ENV_FILE with your production values"
    else
        log_info "Environment file already exists"
    fi
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."

    directories=("logs" "backups" "config" "static" "temp" "monitoring")

    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_success "Created directory: $dir"
        else
            log_info "Directory already exists: $dir"
        fi
    done
}

# Setup logging
setup_logging() {
    log_info "Setting up logging configuration..."

    # Create log files
    touch logs/app.log
    touch logs/access.log
    touch logs/error.log

    # Set proper permissions
    chmod 644 logs/*.log

    log_success "Logging configured"
}

# Run database migrations (if applicable)
run_migrations() {
    log_info "Checking for database migrations..."

    # This is a placeholder for database migration commands
    # Uncomment and modify based on your database setup

    # if [[ -f "migrations/manage.py" ]]; then
    #     source .venv/bin/activate
    #     python migrations/manage.py migrate
    #     log_success "Database migrations completed"
    # else
    #     log_info "No database migrations found"
    # fi
}

# Run production deployment script
run_production_deploy() {
    log_info "Running production deployment script..."

    if [[ -f "production_deploy.py" ]]; then
        source .venv/bin/activate
        python production_deploy.py
        log_success "Production deployment script completed"
    else
        log_error "production_deploy.py not found"
        exit 1
    fi
}

# Start the application
start_application() {
    log_info "Starting NVIDIA Control Panel API..."

    # Check if application is already running
    if pgrep -f "gunicorn.*app_production" > /dev/null; then
        log_warning "Application appears to be already running"
        read -p "Stop existing instance and restart? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            stop_application
        else
            return
        fi
    fi

    # Start with Gunicorn
    source .venv/bin/activate

    if [[ -f "gunicorn.conf.py" ]]; then
        nohup gunicorn --config gunicorn.conf.py app_production:app > logs/gunicorn.log 2>&1 &
        GUNICORN_PID=$!
        echo $GUNICORN_PID > logs/gunicorn.pid
        log_success "Application started with PID: $GUNICORN_PID"
    else
        log_warning "gunicorn.conf.py not found, starting with basic configuration"
        nohup gunicorn --bind 0.0.0.0:$APP_PORT --workers 4 app_production:app > logs/gunicorn.log 2>&1 &
        GUNICORN_PID=$!
        echo $GUNICORN_PID > logs/gunicorn.pid
        log_success "Application started with PID: $GUNICORN_PID"
    fi

    # Wait a moment for startup
    sleep 3

    # Check if process is still running
    if kill -0 $GUNICORN_PID 2>/dev/null; then
        log_success "Application is running successfully"
    else
        log_error "Application failed to start. Check logs/gunicorn.log for details"
        exit 1
    fi
}

# Stop the application
stop_application() {
    log_info "Stopping NVIDIA Control Panel API..."

    if [[ -f "logs/gunicorn.pid" ]]; then
        GUNICORN_PID=$(cat logs/gunicorn.pid)
        if kill -0 $GUNICORN_PID 2>/dev/null; then
            kill $GUNICORN_PID
            log_success "Application stopped (PID: $GUNICORN_PID)"
        else
            log_warning "Application process not found"
        fi
        rm -f logs/gunicorn.pid
    else
        # Try to find and kill gunicorn processes
        if pgrep -f "gunicorn.*app_production" > /dev/null; then
            pkill -f "gunicorn.*app_production"
            log_success "Application processes killed"
        else
            log_info "No application processes found"
        fi
    fi
}

# Check application health
check_health() {
    log_info "Checking application health..."

    max_attempts=10
    attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "http://localhost:$APP_PORT/health" > /dev/null 2>&1; then
            log_success "Application is healthy"
            return 0
        fi

        log_info "Waiting for application to become healthy (attempt $attempt/$max_attempts)..."
        sleep 2
        ((attempt++))
    done

    log_error "Application failed health check after $max_attempts attempts"
    return 1
}

# Show deployment information
show_info() {
    echo
    echo "=================================================="
    echo "🚀 NVIDIA Control Panel API - Deployment Complete!"
    echo "=================================================="
    echo
    echo "📊 Deployment Information:"
    echo "   • Application: $APP_NAME"
    echo "   • Port: $APP_PORT"
    echo "   • Environment: Production"
    echo "   • Virtual Environment: .venv"
    echo
    echo "🔗 Access URLs:"
    echo "   • API: http://localhost:$APP_PORT"
    echo "   • Health Check: http://localhost:$APP_PORT/health"
    echo "   • API Docs: http://localhost:$APP_PORT/api/docs"
    echo "   • Metrics: http://localhost:$APP_PORT/metrics"
    echo
    echo "📁 Important Files:"
    echo "   • Configuration: production_config.json"
    echo "   • Environment: $ENV_FILE"
    echo "   • Logs: logs/app.log"
    echo "   • PID File: logs/gunicorn.pid"
    echo
    echo "🛠️  Management Commands:"
    echo "   • Start: ./deploy.sh start"
    echo "   • Stop: ./deploy.sh stop"
    echo "   • Restart: ./deploy.sh restart"
    echo "   • Health Check: ./deploy.sh health"
    echo "   • Logs: tail -f logs/app.log"
    echo
    echo "🔒 Security Notes:"
    echo "   • Update $ENV_FILE with production secrets"
    echo "   • Configure firewall rules"
    echo "   • Set up SSL/TLS certificates"
    echo "   • Review and update CORS settings"
    echo
    echo "=================================================="
}

# Main deployment function
main() {
    echo "🚀 NVIDIA Control Panel API - Production Deployment"
    echo "=================================================="

    case "${1:-deploy}" in
        "deploy")
            check_root
            check_requirements
            setup_venv
            install_dependencies
            setup_environment
            create_directories
            setup_logging
            run_migrations
            run_production_deploy
            start_application
            check_health
            show_info
            ;;
        "start")
            start_application
            check_health
            ;;
        "stop")
            stop_application
            ;;
        "restart")
            stop_application
            sleep 2
            start_application
            check_health
            ;;
        "health")
            check_health
            ;;
        "logs")
            if [[ -f "logs/app.log" ]]; then
                tail -f logs/app.log
            else
                log_error "Log file not found"
            fi
            ;;
        "status")
            if [[ -f "logs/gunicorn.pid" ]]; then
                GUNICORN_PID=$(cat logs/gunicorn.pid)
                if kill -0 $GUNICORN_PID 2>/dev/null; then
                    log_success "Application is running (PID: $GUNICORN_PID)"
                else
                    log_warning "Application is not running (stale PID file)"
                fi
            else
                log_info "Application is not running"
            fi
            ;;
        *)
            echo "Usage: $0 {deploy|start|stop|restart|health|logs|status}"
            echo
            echo "Commands:"
            echo "  deploy  - Full production deployment"
            echo "  start   - Start the application"
            echo "  stop    - Stop the application"
            echo "  restart - Restart the application"
            echo "  health  - Check application health"
            echo "  logs    - View application logs"
            echo "  status  - Show application status"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
