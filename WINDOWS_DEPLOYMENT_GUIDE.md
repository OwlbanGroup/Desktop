# NVIDIA Control Panel API - Windows Deployment Guide

## 🚀 Windows Production Deployment

This guide provides Windows-specific instructions for deploying the NVIDIA Control Panel Flask API to production environments on Windows systems.

## 📋 Windows System Requirements

### Minimum Requirements
- **Windows**: 10 (64-bit) or Windows Server 2016+
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Stable internet connection

### Required Software
```powershell
# Install Python (if not already installed)
# Download from: https://python.org/downloads/
# Or use Chocolatey:
choco install python --version=3.9.0

# Install Git (optional, for cloning)
choco install git
```

## 🛠️ Windows Deployment Options

### Option 1: PowerShell Deployment (Recommended)

#### 1. Clone and Setup
```powershell
# Clone the repository
git clone <your-repo-url>
cd nvidia-control-panel-api

# Set execution policy (one-time setup)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. Full Production Deployment
```powershell
# Run full deployment
.\deploy.ps1 -Action deploy
```

#### 3. Verify Deployment
```powershell
# Check application status
.\deploy.ps1 -Action status

# Check application health
.\deploy.ps1 -Action health

# View application logs
.\deploy.ps1 -Action logs
```

### Option 2: Command Prompt Deployment

#### 1. Clone and Setup
```cmd
# Clone the repository
git clone <your-repo-url>
cd nvidia-control-panel-api
```

#### 2. Full Production Deployment
```cmd
# Run full deployment
deploy.bat deploy
```

#### 3. Verify Deployment
```cmd
# Check application status
deploy.bat status

# Check application health
deploy.bat health

# View application logs
deploy.bat logs
```

### Option 3: Manual Windows Deployment

#### 1. Setup Python Virtual Environment
```cmd
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

#### 2. Install Dependencies
```cmd
# Install production dependencies
pip install -r requirements.txt
```

#### 3. Configure Environment
```cmd
# Copy environment template
copy .env.example .env

# Edit .env with your production values
notepad .env
```

#### 4. Run Production Deployment Script
```cmd
# Run deployment script
python production_deploy.py
```

#### 5. Start Application
```cmd
# Start with Gunicorn
python -m gunicorn --config gunicorn.conf.py app_production:app
```

## 📁 Windows Project Structure

```
nvidia-control-panel-api/
├── production_deploy.py      # Main deployment script
├── deploy.sh                 # Linux/macOS deployment wrapper
├── deploy.bat                # Windows CMD deployment script
├── deploy.ps1                # Windows PowerShell deployment script
├── production_config.json    # Production configuration
├── requirements.txt          # Python dependencies
├── app_production.py         # Production Flask application
├── gunicorn.conf.py          # Gunicorn configuration
├── logs/                     # Application logs
├── backups/                  # Backup files
└── .env                      # Environment variables
```

## ⚙️ Windows Configuration

### Environment Variables (.env)

Create and configure the `.env` file:

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-change-this
DEBUG=False

# Server Configuration
HOST=0.0.0.0
PORT=8000

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
```

### Windows-Specific Configuration

```json
{
  "app": {
    "name": "nvidia-control-panel-api",
    "version": "1.0.0",
    "host": "0.0.0.0",
    "port": 8000,
    "debug": false,
    "workers": 2,
    "timeout": 30
  },
  "windows": {
    "use_windows_services": false,
    "log_to_event_viewer": false,
    "auto_start": true,
    "service_name": "NVIDIA-Control-Panel-API"
  },
  "security": {
    "secret_key": "your-production-secret-key-change-this",
    "cors_origins": ["http://localhost:3000", "https://yourdomain.com"],
    "rate_limits": {
      "default": "200 per day, 50 per hour",
      "strict": "10 per minute"
    }
  }
}
```

## 🛠️ Windows Management Commands

### PowerShell Commands
```powershell
# Start application
.\deploy.ps1 -Action start

# Stop application
.\deploy.ps1 -Action stop

# Restart application
.\deploy.ps1 -Action restart

# Check status
.\deploy.ps1 -Action status

# View logs
.\deploy.ps1 -Action logs
```

### Command Prompt Commands
```cmd
# Start application
deploy.bat start

# Stop application
deploy.bat stop

# Restart application
deploy.bat restart

# Check status
deploy.bat status

# View logs
deploy.bat logs
```

### Manual Commands
```cmd
# Activate virtual environment
.venv\Scripts\activate

# Start application
python -m gunicorn --bind 0.0.0.0:8000 --workers 2 app_production:app

# Check running processes
tasklist /FI "IMAGENAME eq python.exe"

# Kill specific process
taskkill /PID <PID> /F
```

## 🔗 Windows API Endpoints

Once deployed, the API will be available at:

- **Base URL**: `http://localhost:8000`
- **Health Check**: `http://localhost:8000/health`
- **API Documentation**: `http://localhost:8000/api/docs`
- **Metrics**: `http://localhost:8000/metrics`

### Authentication

All API endpoints require Bearer token authentication:

```cmd
# Using curl (if installed)
curl -H "Authorization: Bearer your-api-token" ^
     http://localhost:8000/api/gpu/status

# Using PowerShell
$headers = @{ "Authorization" = "Bearer your-api-token" }
Invoke-WebRequest -Uri "http://localhost:8000/api/gpu/status" -Headers $headers
```

## 📊 Windows Monitoring & Health

### Health Checks

#### PowerShell
```powershell
# Check application health
.\deploy.ps1 -Action health

# Manual health check
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "Application is healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "Application is not healthy" -ForegroundColor Red
}
```

#### Command Prompt
```cmd
# Check if port is listening
netstat -ano | findstr :8000

# Test health endpoint
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health'; Write-Host 'Status:' $response.StatusCode } catch { Write-Host 'Error: Application not responding' }"
```

### System Monitoring

#### Windows Performance Monitor
```cmd
# Open Performance Monitor
perfmon

# Check CPU and memory usage
typeperf "\Processor(_Total)\% Processor Time" "\Memory\Available MBytes"

# Monitor specific process
typeperf "\Process(python)\% Processor Time" "\Process(python)\Working Set"
```

#### Task Manager
```cmd
# Open Task Manager
taskmgr

# Or use command line
tasklist /FI "IMAGENAME eq python.exe" /V
```

#### Event Viewer
```cmd
# Open Event Viewer
eventvwr

# View application logs
eventvwr /c:Application
```

## 🔒 Windows Security Configuration

### 1. Windows Firewall Configuration

#### PowerShell
```powershell
# Add firewall rule for the application
New-NetFirewallRule -DisplayName "NVIDIA Control Panel API" ^
    -Direction Inbound ^
    -LocalPort 8000 ^
    -Protocol TCP ^
    -Action Allow ^
    -Profile Any

# Check firewall rules
Get-NetFirewallRule | Where-Object { $_.DisplayName -like "*NVIDIA*" }
```

#### Command Prompt
```cmd
# Add firewall rule
netsh advfirewall firewall add rule name="NVIDIA Control Panel API" ^
    dir=in action=allow protocol=TCP localport=8000

# Show firewall rules
netsh advfirewall firewall show rule name="NVIDIA Control Panel API"
```

### 2. Windows Services (Optional)

#### Install as Windows Service
```powershell
# Install NSSM (Non-Sucking Service Manager)
# Download from: https://nssm.cc/download

# Create service
nssm install "NVIDIA-Control-Panel-API" "C:\Python39\python.exe"
nssm set "NVIDIA-Control-Panel-API" AppParameters "-m gunicorn --config gunicorn.conf.py app_production:app"
nssm set "NVIDIA-Control-Panel-API" AppDirectory "C:\path\to\nvidia-control-panel-api"

# Start service
nssm start "NVIDIA-Control-Panel-API"

# Check service status
nssm status "NVIDIA-Control-Panel-API"
```

### 3. SSL/TLS Setup (Recommended)

#### Using Windows Certificate Store
```powershell
# Generate self-signed certificate
$cert = New-SelfSignedCertificate -DnsName "localhost" -CertStoreLocation "cert:\LocalMachine\My"

# Export certificate
Export-Certificate -Cert $cert -FilePath "localhost.crt"

# Configure application to use HTTPS
# Update production_config.json with SSL settings
```

#### Using IIS as Reverse Proxy
```xml
<!-- web.config for IIS reverse proxy -->
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="Reverse Proxy to Flask" stopProcessing="true">
                    <match url="(.*)" />
                    <action type="Rewrite" url="http://localhost:8000/{R:1}" />
                </rule>
            </rules>
        </rewrite>
    </system.webServer>
</configuration>
```

## 🔄 Windows Updates & Maintenance

### Application Updates
```cmd
# Stop application
deploy.bat stop

# Backup current version
xcopy . current_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2% /E /I /H

# Pull latest changes
git pull origin main

# Update dependencies
.venv\Scripts\activate
pip install -r requirements.txt

# Start application
deploy.bat start

# Verify health
deploy.bat health
```

### Windows-Specific Maintenance
```cmd
# Check Windows version and updates
systeminfo | findstr /B /C:"OS"

# Check disk space
wmic logicaldisk get size,freespace,caption

# Clear temporary files
cleanmgr /sagerun:1

# Check Windows services
sc query | findstr "SERVICE_NAME"
```

## 🚨 Windows Troubleshooting

### Common Windows Issues

#### 1. Execution Policy Errors
```powershell
# Fix execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run with bypass
powershell -ExecutionPolicy Bypass -File deploy.ps1 -Action deploy
```

#### 2. Python Path Issues
```cmd
# Check Python installation
python --version

# If python command not found, use full path
C:\Python39\python.exe --version

# Update PATH environment variable
setx PATH "%PATH%;C:\Python39;C:\Python39\Scripts"
```

#### 3. Port Already in Use
```cmd
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process by PID
taskkill /PID <PID> /F

# Or find and kill Python processes
taskkill /IM python.exe /F
```

#### 4. Permission Denied
```cmd
# Run as administrator
runas /user:Administrator "cmd /c deploy.bat deploy"

# Or use PowerShell with elevated privileges
Start-Process powershell -Verb RunAs -ArgumentList "-File deploy.ps1 -Action deploy"
```

#### 5. Virtual Environment Issues
```cmd
# Recreate virtual environment
rmdir /S /Q .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Windows Log Analysis
```cmd
# View application logs
type logs\app.log

# Search for errors
findstr /C:"ERROR" logs\app.log

# Search for specific endpoint
findstr "/api/gpu/status" logs\access.log

# Monitor logs in real-time
powershell -Command "Get-Content logs\app.log -Wait"
```

### Windows Performance Issues
```cmd
# Check memory usage
wmic OS get FreePhysicalMemory /Value

# Check CPU usage
wmic cpu get loadpercentage

# Check disk I/O
typeperf "\PhysicalDisk(_Total)\Disk Reads/sec" "\PhysicalDisk(_Total)\Disk Writes/sec"

# Generate system report
systeminfo > system_report.txt
```

## 🐳 Windows Docker Deployment

### Install Docker Desktop for Windows
```powershell
# Download and install Docker Desktop
# From: https://www.docker.com/products/docker-desktop

# Start Docker service
Start-Service docker
```

### Docker Commands
```cmd
# Build and run with Docker Compose
docker-compose -f docker-compose.production.yml up -d

# Check container status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Stop containers
docker-compose -f docker-compose.production.yml down
```

### Windows Docker Compose Configuration
```yaml
version: '3.8'

services:
  nvidia-control-panel:
    build:
      context: .
      dockerfile: Dockerfile.production
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key
    volumes:
      - ./logs:/app/logs
      - ./backups:/app/backups
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

## 📞 Windows Support & Documentation

### Windows-Specific Resources
- [Python on Windows Documentation](https://docs.python.org/3/using/windows.html)
- [Windows Services Documentation](https://docs.microsoft.com/en-us/windows/win32/services/services)
- [PowerShell Documentation](https://docs.microsoft.com/en-us/powershell/)
- [Windows Firewall Documentation](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-firewall/)

### Getting Help on Windows
1. Check application logs: `type logs\app.log`
2. Verify configuration: `type .env`
3. Test API endpoints: `curl http://localhost:8000/health` (if curl is installed)
4. Check Windows Event Viewer: `eventvwr`
5. Use PowerShell for diagnostics: `Get-Process | Where-Object { $_.ProcessName -like "*python*" }`

### Windows Community Support
- [Stack Overflow - Windows](https://stackoverflow.com/questions/tagged/windows)
- [Microsoft Developer Community](https://developer.microsoft.com/en-us/)
- [Python Windows SIG](https://www.python.org/community/sig/windows/)

---

## 🎯 Windows Next Steps

1. **Configure Production Secrets**: Update `.env` with production values
2. **Setup Windows Firewall**: Configure firewall rules for port 8000
3. **Consider Windows Services**: Set up as a Windows service for auto-start
4. **SSL/TLS Configuration**: Configure HTTPS certificates
5. **Monitoring Setup**: Configure Windows Performance Monitor
6. **Backup Strategy**: Set up automated backups using Windows Task Scheduler

---

**Windows deployment completed successfully!** 🎉

Your NVIDIA Control Panel API is now ready for production deployment on Windows with enterprise-grade features including security, monitoring, and Windows-specific optimizations.
