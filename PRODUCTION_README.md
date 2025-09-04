# NVIDIA Control Panel API - Production Deployment Guide

## 🚀 Overview

This guide provides comprehensive instructions for deploying the NVIDIA Control Panel Flask API to production environments. The deployment system includes automated scripts, configuration management, monitoring, and security features.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: 1GB free space
- **Network**: Stable internet connection for dependency installation

### Operating System Support
- ✅ **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 9+
- ✅ **macOS**: 10.14+ (for development)
- ✅ **Windows**: 10+ with WSL (for development)

### Required Software
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv curl wget

# CentOS/RHEL
sudo yum install python3 python3-pip curl wget
# or
sudo dnf install python3 python3-pip curl wget

# macOS
brew install python3 curl wget
```

## 🛠️ Quick Start

### 1. Clone and Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd nvidia-control-panel-api

# Make deployment script executable
chmod +x deploy.sh
```

### 2. One-Command Deployment
```bash
# Full production deployment
./deploy.sh deploy
```

### 3. Verify Deployment
```bash
# Check application status
./deploy.sh status

# Check application health
./deploy.sh health

# View application logs
./deploy.sh logs
```

## 📁 Project Structure

```
nvidia-control-panel-api/
├── production_deploy.py      # Main deployment script
├── deploy.sh                 # Simple deployment wrapper
├── production_config.json    # Production configuration
├── requirements.txt          # Python dependencies
├── app_production.py         # Production Flask application
├── gunicorn.conf.py          # Gunicorn configuration
├── nginx.conf                # Nginx configuration
├── docker-compose.production.yml  # Docker setup
├── monitoring/               # Monitoring configuration
│   ├── prometheus.yml
│   └── alert_rules.yml
├── logs/                     # Application logs
├── backups/                  # Backup files
└── .env                      # Environment variables
```

## ⚙️ Configuration

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
LOG_FILE=logs/app.log

# Monitoring Configuration
PROMETHEUS_PORT=9090
HEALTH_CHECK_INTERVAL=30
```

### Production Configuration (production_config.json)

```json
{
  "app": {
    "name": "nvidia-control-panel-api",
    "version": "1.0.0",
    "host": "0.0.0.0",
    "port": 8000,
    "debug": false,
    "workers": 4,
    "timeout": 30
  },
  "security": {
    "secret_key": "your-production-secret-key-change-this",
    "cors_origins": ["http://localhost:3000", "https://yourdomain.com"],
    "rate_limits": {
      "default": "200 per day, 50 per hour",
      "strict": "10 per minute"
    }
  },
  "database": {
    "redis_url": "redis://localhost:6379/0",
    "cache_ttl": 300
  },
  "logging": {
    "level": "INFO",
    "file": "logs/app.log",
    "max_size": "10MB",
    "backup_count": 5
  },
  "monitoring": {
    "health_check_interval": 30,
    "metrics_enabled": true,
    "prometheus_port": 9090
  },
  "deployment": {
    "environment": "production",
    "auto_restart": true,
    "log_rotation": true,
    "backup_enabled": true
  }
}
```

## 🚀 Deployment Options

### Option 1: Automated Deployment (Recommended)

```bash
# Full deployment with all components
./deploy.sh deploy

# This will:
# - Check system requirements
# - Setup Python virtual environment
# - Install dependencies
# - Configure environment
# - Create necessary directories
# - Setup logging
# - Run production deployment script
# - Start the application
# - Verify health
```

### Option 2: Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.production.yml up -d

# Check container status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

### Option 3: Manual Deployment

```bash
# 1. Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your values

# 4. Run production deployment
python production_deploy.py

# 5. Start application
gunicorn --config gunicorn.conf.py app_production:app
```

## 🛠️ Management Commands

### Application Control
```bash
# Start application
./deploy.sh start

# Stop application
./deploy.sh stop

# Restart application
./deploy.sh restart

# Check status
./deploy.sh status
```

### Monitoring & Health
```bash
# Health check
./deploy.sh health

# View logs
./deploy.sh logs

# Follow logs in real-time
tail -f logs/app.log

# Check system resources
htop
```

### Log Management
```bash
# View application logs
tail -f logs/app.log

# View access logs
tail -f logs/access.log

# View error logs
tail -f logs/error.log

# Search logs for errors
grep "ERROR" logs/app.log

# Clear old logs (be careful!)
find logs/ -name "*.log" -mtime +30 -delete
```

## 🔗 API Endpoints

Once deployed, the API will be available at:

- **Base URL**: `http://your-server:8000`
- **Health Check**: `http://your-server:8000/health`
- **API Documentation**: `http://your-server:8000/api/docs`
- **Metrics**: `http://your-server:8000/metrics`

### Authentication

All API endpoints require Bearer token authentication:

```bash
curl -H "Authorization: Bearer your-api-token" \
     http://your-server:8000/api/gpu/status
```

## 📊 Monitoring & Metrics

### Prometheus Metrics

The application exposes Prometheus metrics at `/metrics`:

```bash
# Direct access
curl http://your-server:8000/metrics

# Prometheus configuration
# Add to your prometheus.yml:
scrape_configs:
  - job_name: 'nvidia-control-panel'
    static_configs:
      - targets: ['your-server:8000']
    metrics_path: '/metrics'
```

### Health Checks

```bash
# Application health
curl http://your-server:8000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "environment": "production"
}
```

### System Monitoring

```bash
# CPU and memory usage
ps aux | grep gunicorn

# Network connections
netstat -tlnp | grep :8000

# Disk usage
df -h

# Memory usage
free -h
```

## 🔒 Security Configuration

### 1. Update Secrets
```bash
# Generate secure random key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Update in .env file
SECRET_KEY=your-generated-secure-key
API_TOKEN=your-generated-api-token
```

### 2. Configure Firewall
```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 8000
sudo ufw allow 22
sudo ufw --force enable

# firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 3. SSL/TLS Setup (Recommended)
```bash
# Using Let's Encrypt (certbot)
sudo apt-get install certbot
sudo certbot certonly --standalone -d yourdomain.com

# Update nginx.conf with SSL configuration
# Then restart nginx
sudo systemctl restart nginx
```

### 4. Security Headers

The application includes security headers via Nginx:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

## 🔄 Updates & Maintenance

### Application Updates
```bash
# Stop application
./deploy.sh stop

# Backup current version
cp -r . current_backup_$(date +%Y%m%d_%H%M%S)

# Pull latest changes
git pull origin main

# Install new dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Run migrations (if any)
python manage.py migrate

# Start application
./deploy.sh start

# Verify health
./deploy.sh health
```

### Dependency Updates
```bash
# Update Python packages
source .venv/bin/activate
pip install --upgrade -r requirements.txt

# Check for security vulnerabilities
pip audit

# Update specific package
pip install --upgrade flask
```

### Backup Strategy
```bash
# Database backup (if applicable)
# Add your database backup commands here

# Configuration backup
cp .env backups/.env_$(date +%Y%m%d_%H%M%S)
cp production_config.json backups/

# Log rotation
logrotate -f /etc/logrotate.d/nvidia-control-panel
```

## 🐳 Docker Deployment

### Build Custom Image
```bash
# Build production image
docker build -f Dockerfile.production -t nvidia-control-panel:latest .

# Run container
docker run -d \
  --name nvidia-control-panel \
  -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e API_TOKEN=your-api-token \
  nvidia-control-panel:latest
```

### Docker Compose (Recommended)
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

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in configuration
# Edit production_config.json and .env
```

#### 2. Permission Denied
```bash
# Fix log directory permissions
sudo chown -R $USER:$USER logs/
chmod 755 logs/

# Fix virtual environment permissions
sudo chown -R $USER:$USER .venv/
```

#### 3. Import Errors
```bash
# Reinstall dependencies
source .venv/bin/activate
pip install --force-reinstall -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

#### 4. Memory Issues
```bash
# Check memory usage
free -h

# Reduce worker count in gunicorn.conf.py
workers = 2  # Instead of 4

# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 5. Database Connection Issues
```bash
# Check Redis status
redis-cli ping

# Start Redis service
sudo systemctl start redis-server

# Check Redis logs
sudo journalctl -u redis-server -f
```

### Log Analysis
```bash
# Search for errors
grep "ERROR" logs/app.log | tail -10

# Search for specific endpoint
grep "/api/gpu/status" logs/access.log

# Monitor real-time errors
tail -f logs/app.log | grep --line-buffered "ERROR"
```

## 📞 Support & Documentation

### API Documentation
- **Swagger UI**: `http://your-server:8000/api/docs`
- **Health Endpoint**: `http://your-server:8000/health`
- **Metrics Endpoint**: `http://your-server:8000/metrics`

### Additional Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)

### Getting Help
1. Check application logs: `tail -f logs/app.log`
2. Verify configuration: `cat .env`
3. Test API endpoints: `curl http://localhost:8000/health`
4. Check system resources: `htop`

## 📝 Changelog

### Version 1.0.0
- ✅ Initial production deployment
- ✅ Comprehensive API endpoints
- ✅ Security and authentication
- ✅ Monitoring and metrics
- ✅ Docker support
- ✅ Automated deployment scripts

---

## 🎯 Next Steps

1. **Configure Production Secrets**: Update `.env` with production values
2. **Setup SSL/TLS**: Configure HTTPS certificates
3. **Configure Monitoring**: Set up Prometheus and Grafana
4. **Setup Backups**: Configure automated backup strategy
5. **Security Audit**: Review and harden security settings
6. **Performance Tuning**: Optimize based on load testing

---

**Deployment completed successfully!** 🎉

Your NVIDIA Control Panel API is now running in production with enterprise-grade features including security, monitoring, and scalability.
