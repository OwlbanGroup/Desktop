# NVIDIA Control Panel API - PowerShell Production Deployment Script
# This script handles the complete production deployment process on Windows

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("deploy", "start", "stop", "restart", "health", "logs", "status")]
    [string]$Action = "deploy"
)

# Configuration
$APP_NAME = "nvidia-control-panel-api"
$APP_PORT = 8000
$ENV_FILE = ".env"
$VENV_DIR = ".venv"

# Logging functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check system requirements
function Test-Requirements {
    Write-Info "Checking system requirements..."

    # Check Python version
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found"
        }
        Write-Success "Python found: $pythonVersion"
    }
    catch {
        Write-Error "Python is required but not installed."
        exit 1
    }

    # Check pip
    try {
        $pipVersion = pip --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "pip not found"
        }
        Write-Success "pip found"
    }
    catch {
        Write-Error "pip is required but not installed."
        exit 1
    }

    # Check if port is available
    $connections = Get-NetTCPConnection -LocalPort $APP_PORT -ErrorAction SilentlyContinue
    if ($connections) {
        Write-Warning "Port $APP_PORT is already in use"
        $choice = Read-Host "Continue anyway? (y/N)"
        if ($choice -notmatch "^[Yy]$") {
            exit 1
        }
    }
}

# Setup virtual environment
function New-VirtualEnvironment {
    Write-Info "Setting up Python virtual environment..."

    if (-not (Test-Path $VENV_DIR)) {
        python -m venv $VENV_DIR
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create virtual environment"
            exit 1
        }
        Write-Success "Virtual environment created"
    } else {
        Write-Info "Virtual environment already exists"
    }

    # Activate virtual environment
    & "$VENV_DIR\Scripts\Activate.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to activate virtual environment"
        exit 1
    }
    Write-Success "Virtual environment activated"

    # Upgrade pip
    python -m pip install --upgrade pip
    Write-Success "pip upgraded"
}

# Install dependencies
function Install-Dependencies {
    Write-Info "Installing Python dependencies..."

    & "$VENV_DIR\Scripts\Activate.ps1"

    # Install production dependencies
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install dependencies"
        exit 1
    }
    Write-Success "Dependencies installed"

    # Optional: Install monitoring dependencies
    if (Test-Path "requirements-monitoring.txt") {
        pip install -r requirements-monitoring.txt
        Write-Success "Monitoring dependencies installed"
    }
}

# Setup environment configuration
function Set-Environment {
    Write-Info "Setting up environment configuration..."

    # Create .env file if it doesn't exist
    if (-not (Test-Path $ENV_FILE)) {
        $envContent = @"
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
LOG_FILE=logs\app.log

# Monitoring Configuration
PROMETHEUS_PORT=9090
HEALTH_CHECK_INTERVAL=30
"@

        $envContent | Out-File -FilePath $ENV_FILE -Encoding UTF8
        Write-Success "Environment file created: $ENV_FILE"
        Write-Warning "Please update $ENV_FILE with your production values"
    } else {
        Write-Info "Environment file already exists"
    }
}

# Create necessary directories
function New-Directories {
    Write-Info "Creating necessary directories..."

    $directories = @("logs", "backups", "config", "static", "temp", "monitoring")

    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Success "Created directory: $dir"
        } else {
            Write-Info "Directory already exists: $dir"
        }
    }
}

# Setup logging
function Set-Logging {
    Write-Info "Setting up logging configuration..."

    # Create log files
    @("logs\app.log", "logs\access.log", "logs\error.log") | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType File -Path $_ -Force | Out-Null
        }
    }

    Write-Success "Logging configured"
}

# Run production deployment script
function Invoke-ProductionDeploy {
    Write-Info "Running production deployment script..."

    if (Test-Path "production_deploy.py") {
        & "$VENV_DIR\Scripts\Activate.ps1"
        python production_deploy.py
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Production deployment script failed"
            exit 1
        }
        Write-Success "Production deployment script completed"
    } else {
        Write-Error "production_deploy.py not found"
        exit 1
    }
}

# Start the application
function Start-Application {
    Write-Info "Starting NVIDIA Control Panel API..."

    # Check if application is already running
    $existingProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue |
                      Where-Object { $_.MainWindowTitle -like "*gunicorn*" }

    if ($existingProcess) {
        Write-Warning "Application appears to be already running"
        $choice = Read-Host "Stop existing instance and restart? (y/N)"
        if ($choice -match "^[Yy]$") {
            Stop-Application
        }
    }

    # Start with Gunicorn
    & "$VENV_DIR\Scripts\Activate.ps1"

    $logFile = "logs\gunicorn.log"
    if (Test-Path "gunicorn.conf.py") {
        $process = Start-Process -FilePath "python" -ArgumentList "-m", "gunicorn", "--config", "gunicorn.conf.py", "app_production:app" -RedirectStandardOutput $logFile -RedirectStandardError $logFile -NoNewWindow -PassThru
        $gunicornPid = $process.Id
        $gunicornPid | Out-File -FilePath "logs\gunicorn.pid" -Encoding UTF8
        Write-Success "Application started with PID: $gunicornPid"
    } else {
        Write-Warning "gunicorn.conf.py not found, starting with basic configuration"
        $process = Start-Process -FilePath "python" -ArgumentList "-m", "gunicorn", "--bind", "0.0.0.0:$APP_PORT", "--workers", "4", "app_production:app" -RedirectStandardOutput $logFile -RedirectStandardError $logFile -NoNewWindow -PassThru
        $gunicornPid = $process.Id
        $gunicornPid | Out-File -FilePath "logs\gunicorn.pid" -Encoding UTF8
        Write-Success "Application started with PID: $gunicornPid"
    }

    # Wait a moment for startup
    Start-Sleep -Seconds 3

    # Check if process is still running
    $runningProcess = Get-Process -Id $gunicornPid -ErrorAction SilentlyContinue
    if ($runningProcess) {
        Write-Success "Application is running successfully"
    } else {
        Write-Error "Application failed to start. Check logs\gunicorn.log for details"
        exit 1
    }
}

# Stop the application
function Stop-Application {
    Write-Info "Stopping NVIDIA Control Panel API..."

    if (Test-Path "logs\gunicorn.pid") {
        $gunicornPid = Get-Content "logs\gunicorn.pid"
        $process = Get-Process -Id $gunicornPid -ErrorAction SilentlyContinue
        if ($process) {
            Stop-Process -Id $gunicornPid -Force
            Write-Success "Application stopped (PID: $gunicornPid)"
        } else {
            Write-Warning "Application process not found"
        }
        Remove-Item "logs\gunicorn.pid" -Force
    } else {
        # Try to find and kill gunicorn processes
        $gunicornProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue |
                           Where-Object { $_.CommandLine -like "*gunicorn*" }
        foreach ($proc in $gunicornProcesses) {
            Stop-Process -Id $proc.Id -Force
        }
        Write-Success "Application processes killed"
    }
}

# Check application health
function Test-Health {
    Write-Info "Checking application health..."

    $maxAttempts = 10
    $attempt = 1

    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$APP_PORT/health" -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Success "Application is healthy"
                return
            }
        }
        catch {
            # Continue to next attempt
        }

        Write-Info "Waiting for application to become healthy (attempt $attempt/$maxAttempts)..."
        Start-Sleep -Seconds 2
        $attempt++
    }

    Write-Error "Application failed health check after $maxAttempts attempts"
    exit 1
}

# Show deployment information
function Show-Info {
    Write-Host ""
    Write-Host "=================================================="
    Write-Host "🚀 NVIDIA Control Panel API - Deployment Complete!"
    Write-Host "=================================================="
    Write-Host ""
    Write-Host "📊 Deployment Information:"
    Write-Host "   • Application: $APP_NAME"
    Write-Host "   • Port: $APP_PORT"
    Write-Host "   • Environment: Production"
    Write-Host "   • Virtual Environment: $VENV_DIR"
    Write-Host ""
    Write-Host "🔗 Access URLs:"
    Write-Host "   • API: http://localhost:$APP_PORT"
    Write-Host "   • Health Check: http://localhost:$APP_PORT/health"
    Write-Host "   • API Docs: http://localhost:$APP_PORT/api/docs"
    Write-Host "   • Metrics: http://localhost:$APP_PORT/metrics"
    Write-Host ""
    Write-Host "📁 Important Files:"
    Write-Host "   • Configuration: production_config.json"
    Write-Host "   • Environment: $ENV_FILE"
    Write-Host "   • Logs: logs\app.log"
    Write-Host "   • PID File: logs\gunicorn.pid"
    Write-Host ""
    Write-Host "🛠️  Management Commands:"
    Write-Host "   • Start: .\deploy.ps1 -Action start"
    Write-Host "   • Stop: .\deploy.ps1 -Action stop"
    Write-Host "   • Restart: .\deploy.ps1 -Action restart"
    Write-Host "   • Health Check: .\deploy.ps1 -Action health"
    Write-Host "   • Logs: Get-Content logs\app.log"
    Write-Host "   • Status: .\deploy.ps1 -Action status"
    Write-Host ""
    Write-Host "🔒 Security Notes:"
    Write-Host "   • Update $ENV_FILE with production secrets"
    Write-Host "   • Configure firewall rules"
    Write-Host "   • Set up SSL/TLS certificates"
    Write-Host "   • Review and update CORS settings"
    Write-Host ""
    Write-Host "🐳 Docker Deployment:"
    Write-Host "   • docker-compose -f docker-compose.production.yml up -d"
    Write-Host ""
    Write-Host "📊 Monitoring:"
    Write-Host "   • Prometheus: localhost:9090"
    Write-Host "   • Application metrics available at /metrics"
    Write-Host ""
    Write-Host "=================================================="
}

# Main deployment function
function Invoke-Main {
    Write-Host "🚀 NVIDIA Control Panel API - PowerShell Production Deployment"
    Write-Host "=================================================="

    switch ($Action) {
        "deploy" {
            if (Test-Administrator) {
                Write-Warning "Running as administrator. This will install system-wide."
                $choice = Read-Host "Continue? (y/N)"
                if ($choice -notmatch "^[Yy]$") { exit 1 }
            }

            Test-Requirements
            New-VirtualEnvironment
            Install-Dependencies
            Set-Environment
            New-Directories
            Set-Logging
            Invoke-ProductionDeploy
            Start-Application
            Test-Health
            Show-Info
        }
        "start" {
            Start-Application
            Test-Health
        }
        "stop" {
            Stop-Application
        }
        "restart" {
            Stop-Application
            Start-Sleep -Seconds 2
            Start-Application
            Test-Health
        }
        "health" {
            Test-Health
        }
        "logs" {
            if (Test-Path "logs\app.log") {
                Get-Content "logs\app.log"
            } else {
                Write-Error "Log file not found"
            }
        }
        "status" {
            if (Test-Path "logs\gunicorn.pid") {
                $gunicornPid = Get-Content "logs\gunicorn.pid"
                $process = Get-Process -Id $gunicornPid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Success "Application is running (PID: $gunicornPid)"
                } else {
                    Write-Warning "Application is not running (stale PID file)"
                }
            } else {
                Write-Info "Application is not running"
            }
        }
        default {
            Write-Host "Usage: .\deploy.ps1 -Action {deploy|start|stop|restart|health|logs|status}"
            Write-Host ""
            Write-Host "Commands:"
            Write-Host "  deploy  - Full production deployment"
            Write-Host "  start   - Start the application"
            Write-Host "  stop    - Stop the application"
            Write-Host "  restart - Restart the application"
            Write-Host "  health  - Check application health"
            Write-Host "  logs    - View application logs"
            Write-Host "  status  - Show application status"
            exit 1
        }
    }
}

# Run main function
Invoke-Main
