@echo off
REM NVIDIA Control Panel API - Windows Production Deployment Script
REM This script handles the complete production deployment process on Windows

setlocal enabledelayedexpansion

REM Configuration
set "APP_NAME=nvidia-control-panel-api"
set "APP_PORT=8000"
set "ENV_FILE=.env"
set "VENV_DIR=.venv"

REM Colors for output (Windows CMD)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Logging functions
:log_info
echo [%BLUE%INFO%NC%] %~1
goto :eof

:log_success
echo [%GREEN%SUCCESS%NC%] %~1
goto :eof

:log_warning
echo [%YELLOW%WARNING%NC%] %~1
goto :eof

:log_error
echo [%RED%ERROR%NC%] %~1
goto :eof

REM Check if running as administrator
:check_admin
net session >nul 2>&1
if %errorLevel% == 0 (
    call :log_warning "Running as administrator. This will install system-wide."
    set /p choice="Continue? (y/N): "
    if /i not "!choice!"=="y" exit /b 1
) else (
    call :log_info "Running as standard user."
)
goto :eof

REM Check system requirements
:check_requirements
call :log_info "Checking system requirements..."

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Python is required but not installed."
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
call :log_success "Python !PYTHON_VERSION! found"

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    call :log_error "pip is required but not installed."
    exit /b 1
)
call :log_success "pip found"

REM Check if port is available
netstat -an | find ":!APP_PORT! " >nul 2>&1
if !errorlevel! == 0 (
    call :log_warning "Port !APP_PORT! is already in use"
    set /p choice="Continue anyway? (y/N): "
    if /i not "!choice!"=="y" exit /b 1
)
goto :eof

REM Setup virtual environment
:setup_venv
call :log_info "Setting up Python virtual environment..."

if not exist "%VENV_DIR%" (
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        call :log_error "Failed to create virtual environment"
        exit /b 1
    )
    call :log_success "Virtual environment created"
) else (
    call :log_info "Virtual environment already exists"
)

REM Activate virtual environment
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    call :log_error "Failed to activate virtual environment"
    exit /b 1
)
call :log_success "Virtual environment activated"

REM Upgrade pip
python -m pip install --upgrade pip
call :log_success "pip upgraded"
goto :eof

REM Install dependencies
:install_dependencies
call :log_info "Installing Python dependencies..."

call "%VENV_DIR%\Scripts\activate.bat"

REM Install production dependencies
pip install -r requirements.txt
if errorlevel 1 (
    call :log_error "Failed to install dependencies"
    exit /b 1
)
call :log_success "Dependencies installed"

REM Optional: Install monitoring dependencies
if exist "requirements-monitoring.txt" (
    pip install -r requirements-monitoring.txt
    call :log_success "Monitoring dependencies installed"
)
goto :eof

REM Setup environment configuration
:setup_environment
call :log_info "Setting up environment configuration..."

REM Create .env file if it doesn't exist
if not exist "%ENV_FILE%" (
    echo # NVIDIA Control Panel API - Environment Configuration > "%ENV_FILE%"
    echo # Copy this file and update values for your environment >> "%ENV_FILE%"
    echo. >> "%ENV_FILE%"
    echo # Flask Configuration >> "%ENV_FILE%"
    echo FLASK_ENV=production >> "%ENV_FILE%"
    echo SECRET_KEY=your-production-secret-key-change-this >> "%ENV_FILE%"
    echo DEBUG=False >> "%ENV_FILE%"
    echo. >> "%ENV_FILE%"
    echo # Server Configuration >> "%ENV_FILE%"
    echo HOST=0.0.0.0 >> "%ENV_FILE%"
    echo PORT=!APP_PORT! >> "%ENV_FILE%"
    echo. >> "%ENV_FILE%"
    echo # Redis Configuration (optional) >> "%ENV_FILE%"
    echo REDIS_URL=redis://localhost:6379/0 >> "%ENV_FILE%"
    echo. >> "%ENV_FILE%"
    echo # API Configuration >> "%ENV_FILE%"
    echo API_TOKEN=your-production-api-token-change-this >> "%ENV_FILE%"
    echo CORS_ORIGINS=http://localhost:3000,https://yourdomain.com >> "%ENV_FILE%"
    echo. >> "%ENV_FILE%"
    echo # Logging Configuration >> "%ENV_FILE%"
    echo LOG_LEVEL=INFO >> "%ENV_FILE%"
    echo LOG_FILE=logs\app.log >> "%ENV_FILE%"
    echo. >> "%ENV_FILE%"
    echo # Monitoring Configuration >> "%ENV_FILE%"
    echo PROMETHEUS_PORT=9090 >> "%ENV_FILE%"
    echo HEALTH_CHECK_INTERVAL=30 >> "%ENV_FILE%"
    call :log_success "Environment file created: %ENV_FILE%"
    call :log_warning "Please update %ENV_FILE% with your production values"
) else (
    call :log_info "Environment file already exists"
)
goto :eof

REM Create necessary directories
:create_directories
call :log_info "Creating necessary directories..."

set "directories=logs backups config static temp monitoring"

for %%d in (%directories%) do (
    if not exist "%%d" (
        mkdir "%%d" 2>nul
        if !errorlevel! == 0 (
            call :log_success "Created directory: %%d"
        ) else (
            call :log_warning "Failed to create directory: %%d"
        )
    ) else (
        call :log_info "Directory already exists: %%d"
    )
)
goto :eof

REM Setup logging
:setup_logging
call :log_info "Setting up logging configuration..."

REM Create log files
echo. > logs\app.log 2>nul
echo. > logs\access.log 2>nul
echo. > logs\error.log 2>nul

call :log_success "Logging configured"
goto :eof

REM Run production deployment script
:run_production_deploy
call :log_info "Running production deployment script..."

if exist "production_deploy.py" (
    call "%VENV_DIR%\Scripts\activate.bat"
    python production_deploy.py
    if errorlevel 1 (
        call :log_error "Production deployment script failed"
        exit /b 1
    )
    call :log_success "Production deployment script completed"
) else (
    call :log_error "production_deploy.py not found"
    exit /b 1
)
goto :eof

REM Start the application
:start_application
call :log_info "Starting NVIDIA Control Panel API..."

REM Check if application is already running
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq gunicorn*" 2>NUL | find /I /N "python.exe">NUL
if !errorlevel! == 0 (
    call :log_warning "Application appears to be already running"
    set /p choice="Stop existing instance and restart? (y/N): "
    if /i "!choice!"=="y" call :stop_application
)

REM Start with Gunicorn (using python module)
call "%VENV_DIR%\Scripts\activate.bat"

if exist "gunicorn.conf.py" (
    start /B python -m gunicorn --config gunicorn.conf.py app_production:app > logs\gunicorn.log 2>&1
    set GUNICORN_PID=!errorlevel!
    echo !GUNICORN_PID! > logs\gunicorn.pid
    call :log_success "Application started with PID: !GUNICORN_PID!"
) else (
    call :log_warning "gunicorn.conf.py not found, starting with basic configuration"
    start /B python -m gunicorn --bind 0.0.0.0:!APP_PORT! --workers 4 app_production:app > logs\gunicorn.log 2>&1
    set GUNICORN_PID=!errorlevel!
    echo !GUNICORN_PID! > logs\gunicorn.pid
    call :log_success "Application started with PID: !GUNICORN_PID!"
)

REM Wait a moment for startup
timeout /t 3 /nobreak >nul

REM Check if process is still running
tasklist /FI "PID eq !GUNICORN_PID!" 2>NUL | find /I /N "python.exe">NUL
if !errorlevel! == 0 (
    call :log_success "Application is running successfully"
) else (
    call :log_error "Application failed to start. Check logs\gunicorn.log for details"
    exit /b 1
)
goto :eof

REM Stop the application
:stop_application
call :log_info "Stopping NVIDIA Control Panel API..."

if exist "logs\gunicorn.pid" (
    set /p GUNICORN_PID=<logs\gunicorn.pid
    tasklist /FI "PID eq !GUNICORN_PID!" 2>NUL | find /I /N "python.exe">NUL
    if !errorlevel! == 0 (
        taskkill /PID !GUNICORN_PID! /F >nul 2>&1
        call :log_success "Application stopped (PID: !GUNICORN_PID!)"
    ) else (
        call :log_warning "Application process not found"
    )
    del logs\gunicorn.pid 2>nul
) else (
    REM Try to find and kill gunicorn processes
    for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" ^| find "python.exe"') do (
        taskkill /PID %%i /F >nul 2>&1
    )
    call :log_success "Application processes killed"
)
goto :eof

REM Check application health
:check_health
call :log_info "Checking application health..."

set /a max_attempts=10
set /a attempt=1

:health_loop
if !attempt! gtr !max_attempts! goto health_failed

powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:!APP_PORT!/health' -TimeoutSec 10; if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if !errorlevel! == 0 (
    call :log_success "Application is healthy"
    goto :eof
)

call :log_info "Waiting for application to become healthy (attempt !attempt!/!max_attempts!)..."
timeout /t 2 /nobreak >nul
set /a attempt+=1
goto health_loop

:health_failed
call :log_error "Application failed health check after !max_attempts! attempts"
exit /b 1

REM Show deployment information
:show_info
echo.
echo ===================================================
echo ^|                                                ^|
echo ^|  🚀 NVIDIA Control Panel API - Deployment Complete!  ^|
echo ^|                                                ^|
echo ===================================================
echo.
echo 📊 Deployment Information:
echo    • Application: !APP_NAME!
echo    • Port: !APP_PORT!
echo    • Environment: Production
echo    • Virtual Environment: !VENV_DIR!
echo.
echo 🔗 Access URLs:
echo    • API: http://localhost:!APP_PORT!
echo    • Health Check: http://localhost:!APP_PORT!/health
echo    • API Docs: http://localhost:!APP_PORT!/api/docs
echo    • Metrics: http://localhost:!APP_PORT!/metrics
echo.
echo 📁 Important Files:
echo    • Configuration: production_config.json
echo    • Environment: !ENV_FILE!
echo    • Logs: logs\app.log
echo    • PID File: logs\gunicorn.pid
echo.
echo 🛠️  Management Commands:
echo    • Start: deploy.bat start
echo    • Stop: deploy.bat stop
echo    • Restart: deploy.bat restart
echo    • Health Check: deploy.bat health
echo    • Logs: type logs\app.log
echo    • Status: deploy.bat status
echo.
echo 🔒 Security Notes:
echo    • Update !ENV_FILE! with production secrets
echo    • Configure firewall rules
echo    • Set up SSL/TLS certificates
echo    • Review and update CORS settings
echo.
echo 🐳 Docker Deployment:
echo    • docker-compose -f docker-compose.production.yml up -d
echo.
echo 📊 Monitoring:
echo    • Prometheus: localhost:9090
echo    • Application metrics available at /metrics
echo.
echo ===================================================
goto :eof

REM Main deployment function
:main
echo 🚀 NVIDIA Control Panel API - Windows Production Deployment
echo ===================================================

if "%1"=="" goto deploy
if "%1"=="deploy" goto deploy
if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="health" goto health
if "%1"=="logs" goto logs
if "%1"=="status" goto status
goto usage

:deploy
call :check_admin
call :check_requirements
call :setup_venv
call :install_dependencies
call :setup_environment
call :create_directories
call :setup_logging
call :run_production_deploy
call :start_application
call :check_health
call :show_info
goto :eof

:start
call :start_application
call :check_health
goto :eof

:stop
call :stop_application
goto :eof

:restart
call :stop_application
timeout /t 2 /nobreak >nul
call :start_application
call :check_health
goto :eof

:health
call :check_health
goto :eof

:logs
if exist "logs\app.log" (
    type logs\app.log
) else (
    call :log_error "Log file not found"
)
goto :eof

:status
if exist "logs\gunicorn.pid" (
    set /p GUNICORN_PID=<logs\gunicorn.pid
    tasklist /FI "PID eq !GUNICORN_PID!" 2>NUL | find /I /N "python.exe">NUL
    if !errorlevel! == 0 (
        call :log_success "Application is running (PID: !GUNICORN_PID!)"
    ) else (
        call :log_warning "Application is not running (stale PID file)"
    )
) else (
    call :log_info "Application is not running"
)
goto :eof

:usage
echo Usage: %0 {deploy^|start^|stop^|restart^|health^|logs^|status}
echo.
echo Commands:
echo   deploy  - Full production deployment
echo   start   - Start the application
echo   stop    - Stop the application
echo   restart - Restart the application
echo   health  - Check application health
echo   logs    - View application logs
echo   status  - Show application status
goto :eof

REM Run main function
call :main %1
