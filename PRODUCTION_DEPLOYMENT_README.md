# OSCAR-BROOME-REVENUE Production Deployment Guide

This guide provides comprehensive instructions for deploying the OSCAR-BROOME-REVENUE integrated financial platform to production environments.

## 🚀 Quick Start

```bash
# Deploy to production
python production_deploy_script.py --environment production --version 1.0.0

# Deploy to staging
python production_deploy_script.py --environment staging --version 1.0.0-beta

# Dry run (validation only)
python production_deploy_script.py --environment production --version 1.0.0 --dry-run
```

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Node.js**: 16.x or higher
- **Docker**: 20.x or higher
- **Docker Compose**: 2.x or higher
- **PostgreSQL**: 13.x or higher (for database)
- **Redis**: 6.x or higher (for caching)

### Environment Variables
Set the following environment variables before deployment:

```bash
# Database Configuration
export DATABASE_URL="postgresql://username:password@localhost:5432/owlban_db"

# Security Keys
export SECRET_KEY="your-super-secret-key-here"
export JWT_SECRET_KEY="your-jwt-secret-key-here"

# API Keys
export JPMORGAN_API_KEY="your-jpmorgan-api-key"
export NVIDIA_API_KEY="your-nvidia-api-key"
export REDIS_URL="redis://localhost:6379"

# Authentication
export EMERGENCY_OVERRIDE_CODE="OSCAR_BROOME_EMERGENCY_2024"
export ADMIN_OVERRIDE_CODE="ADMIN_OVERRIDE_2024"

# Email Configuration (optional)
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
```

## 🏗️ Deployment Architecture

```
OSCAR-BROOME-REVENUE Production Stack
├── Backend (Flask + SQLAlchemy)
│   ├── API Server (Gunicorn)
│   ├── Database (PostgreSQL)
│   └── Cache (Redis)
├── Frontend (React/Node.js)
│   ├── Web Application
│   └── Static Assets
├── Monitoring (Prometheus + Grafana)
│   ├── Metrics Collection
│   ├── Alerting
│   └── Dashboards
└── Load Balancer (Nginx)
    ├── SSL Termination
    ├── Rate Limiting
    └── Reverse Proxy
```

## 📁 Project Structure

```
production-deployment/
├── production_deploy_script.py    # Main deployment script
├── database/
│   ├── init_db.py                # Database initialization
│   ├── models.py                 # SQLAlchemy models
│   └── seed_data/                # Initial data
├── backend/
│   ├── app_server.py            # Flask application
│   └── security_config.py        # Security configuration
├── OSCAR-BROOME-REVENUE/         # Frontend application
├── monitoring/                   # Monitoring stack
├── production_config.json        # Deployment configuration
└── docker-compose.yml           # Container orchestration
```

## ⚙️ Configuration Files

### production_config.json
```json
{
  "environment": "production",
  "database": {
    "host": "localhost",
    "port": 5432,
    "name": "owlban_db",
    "pool_size": 10,
    "max_overflow": 20
  },
  "backend": {
    "host": "0.0.0.0",
    "port": 5000,
    "workers": 4,
    "timeout": 30
  },
  "frontend": {
    "host": "0.0.0.0",
    "port": 3000,
    "build_command": "npm run build",
    "start_command": "npm start"
  },
  "monitoring": {
    "prometheus_port": 9090,
    "grafana_port": 3001,
    "alertmanager_port": 9093
  }
}
```

## 🚀 Deployment Process

### Phase 1: Environment Validation
- ✅ Check system prerequisites
- ✅ Validate environment variables
- ✅ Test database connectivity
- ✅ Verify file permissions

### Phase 2: Backup Creation
- 💾 Create database backup
- 📁 Backup configuration files
- 📦 Archive current deployment

### Phase 3: Database Setup
- 🗄️ Run database migrations
- 🌱 Populate seed data
- ⚙️ Configure indexes and triggers

### Phase 4: Backend Deployment
- 📦 Install Python dependencies
- 🧪 Run backend tests
- 🚀 Start Flask application with Gunicorn

### Phase 5: Frontend Deployment
- 📦 Install Node.js dependencies
- 🏗️ Build React application
- 🌐 Serve static assets

### Phase 6: Monitoring Setup
- 📊 Deploy Prometheus stack
- 📈 Configure Grafana dashboards
- 🚨 Setup alerting rules

### Phase 7: Health Checks
- 🏥 Test backend API endpoints
- 🌐 Verify frontend accessibility
- 📊 Validate monitoring metrics

## 🔧 Manual Deployment Steps

If you prefer manual deployment or need to troubleshoot:

### 1. Database Setup
```bash
# Initialize database
python database/init_db.py

# Run migrations
alembic upgrade head
```

### 2. Backend Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Start server
gunicorn -w 4 -b 0.0.0.0:5000 backend.app_server:app
```

### 3. Frontend Deployment
```bash
cd OSCAR-BROOME-REVENUE

# Install dependencies
npm install

# Build application
npm run build

# Start server
npm start
```

### 4. Monitoring Setup
```bash
cd monitoring

# Start monitoring stack
docker-compose up -d
```

## 📊 Monitoring & Observability

### Health Check Endpoints
- Backend: `http://localhost:5000/health`
- Frontend: `http://localhost:3000`
- Database: `http://localhost:5432` (connection test)

### Monitoring Dashboards
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`
- Alert Manager: `http://localhost:9093`

### Key Metrics
- API Response Times
- Database Connection Pool
- Memory Usage
- Error Rates
- User Sessions

## 🔒 Security Features

### Authentication & Authorization
- JWT token-based authentication
- Multi-factor authentication (MFA)
- Role-based access control (RBAC)
- Emergency override mechanisms

### Data Protection
- SSL/TLS encryption
- Database connection encryption
- Sensitive data encryption at rest
- Secure API key management

### Network Security
- Rate limiting
- CORS configuration
- Security headers
- Input validation and sanitization

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Test connection
psql -h localhost -U username -d owlban_db

# Reset database
python database/init_db.py --reset
```

#### Backend Service Won't Start
```bash
# Check logs
tail -f production_deploy.log

# Test Flask app directly
python backend/app_server.py

# Check dependencies
pip list | grep -E "(flask|gunicorn)"
```

#### Frontend Build Fails
```bash
cd OSCAR-BROOME-REVENUE

# Clear cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version
npm --version
```

#### Monitoring Stack Issues
```bash
cd monitoring

# Check container status
docker-compose ps

# View logs
docker-compose logs prometheus
docker-compose logs grafana

# Restart services
docker-compose restart
```

### Rollback Procedure
```bash
# Stop all services
docker-compose down

# Restore from backup
python production_deploy_script.py --rollback

# Or manual rollback
# 1. Stop services
# 2. Restore database from backup
# 3. Restore configuration files
# 4. Restart services
```

## 📈 Performance Optimization

### Database Optimization
- Connection pooling configuration
- Query optimization and indexing
- Database partitioning strategy
- Backup and recovery procedures

### Application Performance
- Gunicorn worker configuration
- Caching strategy (Redis)
- Static file optimization
- API rate limiting

### Infrastructure Scaling
- Horizontal scaling with load balancer
- Database read replicas
- CDN for static assets
- Auto-scaling policies

## 🔄 Continuous Integration/Deployment

### GitHub Actions Workflow
```yaml
name: Production Deployment
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Production
        run: |
          python production_deploy_script.py --environment production --version ${{ github.sha }}
```

### Automated Testing
```bash
# Run all tests
python -m pytest tests/ -v --cov=backend --cov-report=html

# Integration tests
python -m pytest tests/test_integration_full.py -v

# Performance tests
python -m pytest tests/test_performance.py -v
```

## 📞 Support & Maintenance

### Regular Maintenance Tasks
- Database backups (daily)
- Log rotation (weekly)
- Security updates (monthly)
- Performance monitoring (continuous)

### Emergency Contacts
- Technical Lead: tech-lead@oscar-broome.com
- DevOps Team: devops@oscar-broome.com
- Security Team: security@oscar-broome.com

### Documentation Updates
- Keep this guide current
- Update API documentation
- Maintain runbooks for common procedures

---

## 🎯 Success Metrics

- **Deployment Time**: < 15 minutes
- **Uptime**: > 99.9%
- **Response Time**: < 500ms (API), < 2s (Frontend)
- **Error Rate**: < 0.1%
- **Security Score**: A+ (SSL Labs)

For additional support or questions, please contact the DevOps team.
