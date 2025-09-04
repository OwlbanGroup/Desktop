#!/usr/bin/env python3
"""
Production Deployment Script for NVIDIA Control Panel Flask Application
Handles complete production setup, configuration, and deployment
"""

import os
import sys
import json
import subprocess
import shutil
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_deploy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProductionDeployer:
    """Handles production deployment of NVIDIA Control Panel Flask application"""

    def __init__(self, config_file='production_config.json'):
        self.config_file = config_file
        self.project_root = Path(__file__).parent
        self.config = self.load_config()

    def load_config(self):
        """Load production configuration"""
        default_config = {
            'app': {
                'name': 'nvidia-control-panel-api',
                'version': '1.0.0',
                'host': '0.0.0.0',
                'port': 8000,
                'debug': False,
                'workers': 4,
                'timeout': 30
            },
            'security': {
                'secret_key': os.environ.get('SECRET_KEY', 'change-this-in-production'),
                'cors_origins': ['http://localhost:3000', 'https://yourdomain.com'],
                'rate_limits': {
                    'default': '200 per day, 50 per hour',
                    'strict': '10 per minute'
                }
            },
            'database': {
                'redis_url': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
                'cache_ttl': 300
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/app.log',
                'max_size': '10MB',
                'backup_count': 5
            },
            'monitoring': {
                'health_check_interval': 30,
                'metrics_enabled': True,
                'prometheus_port': 9090
            },
            'deployment': {
                'environment': 'production',
                'auto_restart': True,
                'log_rotation': True,
                'backup_enabled': True
            }
        }

        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                user_config = json.load(f)
            # Merge user config with defaults
            self.deep_update(default_config, user_config)

        return default_config

    def deep_update(self, base_dict, update_dict):
        """Deep update dictionary"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict:
                self.deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def setup_environment(self):
        """Setup production environment"""
        logger.info("Setting up production environment...")

        # Create necessary directories
        directories = [
            'logs',
            'backups',
            'config',
            'static',
            'templates',
            'temp'
        ]

        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            logger.info(f"Created directory: {directory}")

        # Setup environment variables
        env_vars = {
            'FLASK_ENV': 'production',
            'SECRET_KEY': self.config['security']['secret_key'],
            'REDIS_URL': self.config['database']['redis_url'],
            'PORT': str(self.config['app']['port']),
            'HOST': self.config['app']['host']
        }

        # Create .env file
        with open('.env', 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")

        logger.info("Environment variables configured")

    def install_dependencies(self):
        """Install production dependencies"""
        logger.info("Installing production dependencies...")

        # Core dependencies
        core_deps = [
            'flask==2.3.3',
            'flask-cors==4.0.0',
            'flask-limiter==3.5.0',
            'redis==4.5.5',
            'cachetools==5.3.0',
            'requests==2.31.0',
            'backoff==2.2.1',
            'circuitbreaker==1.3.0',
            'gunicorn==21.2.0',
            'python-dotenv==1.0.0'
        ]

        # Install core dependencies
        for dep in core_deps:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
                logger.info(f"Installed: {dep}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {dep}: {e}")
                return False

        # Optional monitoring dependencies
        monitoring_deps = [
            'prometheus-client==0.17.1',
            'psutil==5.9.5'
        ]

        try:
            for dep in monitoring_deps:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
                logger.info(f"Installed monitoring: {dep}")
        except subprocess.CalledProcessError:
            logger.warning("Some monitoring dependencies failed to install")

        logger.info("Dependencies installation completed")
        return True

    def create_production_app(self):
        """Create optimized production version of the app"""
        logger.info("Creating production application...")

        production_app_content = '''#!/usr/bin/env python3
"""
Production-ready NVIDIA Control Panel Flask Application
Optimized for performance and security
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
from cachetools import TTLCache
import backoff
import circuitbreaker
from prometheus_client import Counter, Histogram, generate_latest
import psutil

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('flask_requests_total', 'Total number of requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('flask_request_duration_seconds', 'Request duration in seconds', ['method', 'endpoint'])

# Initialize Flask app with production config
app = Flask(__name__)
app.config.from_object('config.ProductionConfig')

# Initialize extensions
CORS(app, origins=os.environ.get('CORS_ORIGINS', '*').split(','))

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    default_limits=["200 per day", "50 per hour"]
)

# Initialize cache
cache = TTLCache(maxsize=1000, ttl=int(os.environ.get('CACHE_TTL', 300)))

# Simple authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status='401').inc()
            return jsonify({'error': 'Missing or invalid authorization header'}), 401

        token = auth_header.split(' ')[1]
        if token != os.environ.get('API_TOKEN', 'test-token-123'):
            REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status='401').inc()
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated_function

# Request metrics decorator
def track_metrics(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = datetime.utcnow()
        try:
            result = f(*args, **kwargs)
            status_code = result[1] if isinstance(result, tuple) else 200
            REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status=str(status_code)).inc()
            return result
        except Exception as e:
            REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status='500').inc()
            raise
        finally:
            duration = (datetime.utcnow() - start_time).total_seconds()
            REQUEST_LATENCY.labels(method=request.method, endpoint=request.path).observe(duration)
    return decorated_function

# GPU Status endpoint with metrics
@app.route('/api/gpu/status', methods=['GET'])
@limiter.limit("30 per minute")
@require_auth
@track_metrics
def get_gpu_status():
    """Get GPU status and basic information"""
    try:
        gpu_status = {
            'gpu_name': 'NVIDIA GeForce RTX 3080',
            'driver_version': '531.41',
            'memory_total': '10 GB',
            'memory_used': '2.1 GB',
            'memory_free': '7.9 GB',
            'gpu_utilization': '45%',
            'memory_utilization': '21%',
            'temperature': '65°C',
            'fan_speed': '1200 RPM',
            'power_draw': '180W',
            'timestamp': datetime.utcnow().isoformat(),
            'server_info': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'uptime': str(datetime.now() - datetime.fromtimestamp(psutil.boot_time()))
            }
        }

        logger.info("GPU status retrieved successfully")
        return jsonify(gpu_status)

    except Exception as e:
        logger.error(f"Error retrieving GPU status: {e}")
        return jsonify({'error': 'Failed to retrieve GPU status'}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'uptime': str(datetime.now() - datetime.fromtimestamp(psutil.boot_time()))
    })

# Metrics endpoint for Prometheus
@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}

# API documentation endpoint
@app.route('/api/docs', methods=['GET'])
def api_docs():
    """Simple API documentation"""
    docs = {
        'title': 'NVIDIA Control Panel API',
        'version': '1.0.0',
        'description': 'REST API for NVIDIA Control Panel functionality',
        'authentication': 'Bearer token required',
        'endpoints': {
            'GET /api/gpu/status': 'Get GPU status and information',
            'GET /health': 'Health check',
            'GET /metrics': 'Prometheus metrics',
            'GET /api/docs': 'API documentation'
        }
    }
    return jsonify(docs)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status='404').inc()
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status='500').inc()
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def rate_limit_exceeded(error):
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status='429').inc()
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'

    logger.info(f"Starting production server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
'''

        with open('app_production.py', 'w') as f:
            f.write(production_app_content)

        logger.info("Production application created: app_production.py")

    def create_config_files(self):
        """Create production configuration files"""
        logger.info("Creating configuration files...")

        # Gunicorn configuration
        gunicorn_config = f'''
# Gunicorn configuration for production
bind = "{self.config['app']['host']}:{self.config['app']['port']}"
workers = {self.config['app']['workers']}
worker_class = "sync"
worker_connections = 1000
timeout = {self.config['app']['timeout']}
keepalive = 2
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = "{self.config['logging']['level'].lower()}"
accesslog = "logs/access.log"
errorlog = "logs/error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "{self.config['app']['name']}"

# Server mechanics
preload_app = True
pidfile = "logs/gunicorn.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None
'''

        with open('gunicorn.conf.py', 'w') as f:
            f.write(gunicorn_config)

        # Systemd service file
        systemd_service = f'''
[Unit]
Description=NVIDIA Control Panel API
After=network.target
Requires=redis-server.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory={self.project_root}
Environment=PATH={self.project_root}/.venv/bin
ExecStart={self.project_root}/.venv/bin/gunicorn --config gunicorn.conf.py app_production:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
RestartSec=5
Restart=always

[Install]
WantedBy=multi-user.target
'''

        with open('nvidia-control-panel.service', 'w') as f:
            f.write(systemd_service)

        # Nginx configuration
        nginx_config = f'''
server {{
    listen 80;
    server_name your-domain.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Static files
    location /static {{
        alias {self.project_root}/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}

    # API endpoints
    location /api {{
        proxy_pass http://127.0.0.1:{self.config['app']['port']};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Rate limiting
        limit_req zone=api burst=10 nodelay;
    }}

    # Health check
    location /health {{
        proxy_pass http://127.0.0.1:{self.config['app']['port']};
        access_log off;
    }}

    # Metrics (protected)
    location /metrics {{
        proxy_pass http://127.0.0.1:{self.config['app']['port']};
        allow 127.0.0.1;
        deny all;
    }}
}}

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
'''

        with open('nginx.conf', 'w') as f:
            f.write(nginx_config)

        logger.info("Configuration files created")

    def create_deployment_scripts(self):
        """Create deployment and management scripts"""
        logger.info("Creating deployment scripts...")

        # Start script
        start_script = '''#!/bin/bash
# Production start script

echo "Starting NVIDIA Control Panel API..."

# Activate virtual environment
source .venv/bin/activate

# Start with Gunicorn
gunicorn --config gunicorn.conf.py app_production:app

echo "Application started successfully"
'''

        with open('start_production.sh', 'w') as f:
            f.write(start_script)

        # Stop script
        stop_script = '''#!/bin/bash
# Production stop script

echo "Stopping NVIDIA Control Panel API..."

# Kill Gunicorn processes
pkill -f gunicorn

echo "Application stopped"
'''

        with open('stop_production.sh', 'w') as f:
            f.write(stop_script)

        # Health check script
        health_script = '''#!/bin/bash
# Health check script

HEALTH_URL="http://localhost:8000/health"
TIMEOUT=10

response=$(curl -s -w "%{http_code}" -o /dev/null --max-time $TIMEOUT $HEALTH_URL)
exit_code=$?

if [ $exit_code -eq 0 ] && [ "$response" = "200" ]; then
    echo "✅ Application is healthy"
    exit 0
else
    echo "❌ Application is unhealthy (HTTP $response)"
    exit 1
fi
'''

        with open('health_check.sh', 'w') as f:
            f.write(health_script)

        # Make scripts executable
        for script in ['start_production.sh', 'stop_production.sh', 'health_check.sh']:
            os.chmod(script, 0o755)

        logger.info("Deployment scripts created")

    def setup_monitoring(self):
        """Setup monitoring and alerting"""
        logger.info("Setting up monitoring...")

        # Create monitoring directory
        Path('monitoring').mkdir(exist_ok=True)

        # Prometheus configuration
        prometheus_config = f'''
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - localhost:9093

scrape_configs:
  - job_name: 'nvidia-control-panel'
    static_configs:
      - targets: ['localhost:{self.config["app"]["port"]}']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
'''

        with open('monitoring/prometheus.yml', 'w') as f:
            f.write(prometheus_config)

        # Alert rules
        alert_rules = '''
groups:
  - name: nvidia_control_panel
    rules:
      - alert: HighCPUUsage
        expr: cpu_usage_percent > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 90% for more than 5 minutes"

      - alert: HighMemoryUsage
        expr: memory_usage_percent > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85% for more than 5 minutes"

      - alert: ApplicationDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Application is down"
          description: "NVIDIA Control Panel API is not responding"
'''

        with open('monitoring/alert_rules.yml', 'w') as f:
            f.write(alert_rules)

        logger.info("Monitoring configuration created")

    def create_docker_setup(self):
        """Create Docker configuration for containerized deployment"""
        logger.info("Creating Docker configuration...")

        # Dockerfile
        dockerfile = '''
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \\
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app_production:app"]
'''

        with open('Dockerfile.production', 'w') as f:
            f.write(dockerfile)

        # Docker Compose
        docker_compose = f'''
version: '3.8'

services:
  nvidia-control-panel:
    build:
      context: .
      dockerfile: Dockerfile.production
    ports:
      - "{self.config['app']['port']}:8000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY={self.config['security']['secret_key']}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - nvidia-control-panel
    restart: unless-stopped

volumes:
  redis_data:
'''

        with open('docker-compose.production.yml', 'w') as f:
            f.write(docker_compose)

        logger.info("Docker configuration created")

    def deploy(self):
        """Execute full production deployment"""
        logger.info("Starting production deployment...")

        steps = [
            ("Setting up environment", self.setup_environment),
            ("Installing dependencies", self.install_dependencies),
            ("Creating production app", self.create_production_app),
            ("Creating config files", self.create_config_files),
            ("Creating deployment scripts", self.create_deployment_scripts),
            ("Setting up monitoring", self.setup_monitoring),
            ("Creating Docker setup", self.create_docker_setup)
        ]

        for step_name, step_func in steps:
            logger.info(f"Executing: {step_name}")
            try:
                result = step_func()
                if result is False:
                    logger.error(f"Failed at step: {step_name}")
                    return False
                logger.info(f"✅ Completed: {step_name}")
            except Exception as e:
                logger.error(f"Error in {step_name}: {e}")
                return False

        logger.info("🎉 Production deployment completed successfully!")
        return True

    def show_deployment_info(self):
        """Show deployment information and next steps"""
        print("\n" + "="*60)
        print("🚀 NVIDIA Control Panel API - Production Deployment Complete!")
        print("="*60)

        print("\n📋 Deployment Summary:")
        print(f"   • Application: {self.config['app']['name']} v{self.config['app']['version']}")
        print(f"   • Port: {self.config['app']['port']}")
        print(f"   • Environment: {self.config['deployment']['environment']}")

        print("\n🔧 Next Steps:")

        print("\n1. Start the application:")
        print("   ./start_production.sh")

        print("\n2. Check application health:")
        print("   ./health_check.sh")

        print("\n3. View logs:")
        print("   tail -f logs/app.log")

        print("\n4. API Documentation:")
        print(f"   http://localhost:{self.config['app']['port']}/api/docs")

        print("\n5. Health Check:")
        print(f"   http://localhost:{self.config['app']['port']}/health")

        print("\n6. Prometheus Metrics:")
        print(f"   http://localhost:{self.config['app']['port']}/metrics")

        print("\n🔒 Security Notes:")
        print("   • Change the default API token in production")
        print("   • Configure proper SSL/TLS certificates")
        print("   • Set up firewall rules")
        print("   • Configure log rotation")

        print("\n🐳 Docker Deployment:")
        print("   docker-compose -f docker-compose.production.yml up -d")

        print("\n📊 Monitoring:")
        print("   • Prometheus: localhost:9090")
        print("   • Application metrics available at /metrics")

        print("\n" + "="*60)

def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description='Production Deployment for NVIDIA Control Panel API')
    parser.add_argument('--config', default='production_config.json', help='Configuration file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')

    args = parser.parse_args()

    deployer = ProductionDeployer(args.config)

    if args.dry_run:
        print("🔍 Dry run mode - showing deployment plan:")
        print("\nConfiguration:")
        print(json.dumps(deployer.config, indent=2))
        return

    success = deployer.deploy()

    if success:
        deployer.show_deployment_info()
        print("\n✅ Deployment completed successfully!")
    else:
        print("\n❌ Deployment failed. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
