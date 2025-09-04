#!/usr/bin/env python3
"""
Production Orchestrator for OWLban Project
Coordinates all production readiness components and deployment
"""

import os
import sys
import json
import argparse
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProductionOrchestrator:
    """Orchestrates all production components and deployment"""

    def __init__(self, config_file='production_config.json'):
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / config_file
        self.config = self.load_config()
        self.components = {
            'database': False,
            'ssl': False,
            'load_balancer': False,
            'monitoring': False,
            'backup': False,
            'deployment': False
        }

    def load_config(self) -> Dict:
        """Load production configuration"""
        default_config = {
            'environment': 'production',
            'database': {
                'url': 'postgresql://owlban:password@localhost:5432/owlban_db',
                'migrations_enabled': True
            },
            'ssl': {
                'enabled': True,
                'cert_path': '/etc/ssl/certs/owlban.crt',
                'key_path': '/etc/ssl/private/owlban.key',
                'ca_cert_path': '/etc/ssl/certs/ca.crt'
            },
            'load_balancer': {
                'enabled': True,
                'nginx_config': 'load_balancer/nginx.conf',
                'upstream_servers': ['localhost:8000', 'localhost:8001']
            },
            'monitoring': {
                'enabled': True,
                'prometheus_port': 9090,
                'alertmanager_port': 9093,
                'grafana_port': 3000
            },
            'backup': {
                'enabled': True,
                'schedule': 'daily',
                'retention_days': 30
            },
            'deployment': {
                'method': 'docker-compose',
                'replicas': 2,
                'health_check_timeout': 300
            }
        }

        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                user_config = json.load(f)
            self.deep_update(default_config, user_config)

        return default_config

    def deep_update(self, base_dict: Dict, update_dict: Dict):
        """Deep update dictionary"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict:
                self.deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def run_command(self, command: str, cwd: Optional[Path] = None) -> bool:
        """Run shell command and return success status"""
        try:
            logger.info(f"Executing: {command}")
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                logger.info(f"✅ Command succeeded: {command}")
                return True
            else:
                logger.error(f"❌ Command failed: {command}")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Command timed out: {command}")
            return False
        except Exception as e:
            logger.error(f"❌ Command error: {e}")
            return False

    def setup_database(self) -> bool:
        """Setup database with migrations and initial data"""
        logger.info("🔧 Setting up database...")

        try:
            # Test database connection
            if not self.run_command("python database/migrations.py test"):
                return False

            # Initialize database
            if not self.run_command("python database/migrations.py setup"):
                return False

            self.components['database'] = True
            logger.info("✅ Database setup completed")
            return True

        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            return False

    def setup_ssl(self) -> bool:
        """Setup SSL certificates"""
        logger.info("🔐 Setting up SSL certificates...")

        if not self.config['ssl']['enabled']:
            logger.info("ℹ️  SSL setup skipped (disabled in config)")
            self.components['ssl'] = True
            return True

        try:
            # Generate self-signed certificates for development
            ssl_script = """
#!/bin/bash
# Generate SSL certificates
openssl req -x509 -newkey rsa:4096 -keyout ssl.key -out ssl.crt -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
mkdir -p ssl
mv ssl.key ssl/ssl.key
mv ssl.crt ssl/ssl.crt
chmod 600 ssl/ssl.key
"""

            with open('generate_ssl.sh', 'w') as f:
                f.write(ssl_script)

            if not self.run_command("chmod +x generate_ssl.sh && ./generate_ssl.sh"):
                return False

            # Clean up
            os.remove('generate_ssl.sh')

            self.components['ssl'] = True
            logger.info("✅ SSL setup completed")
            return True

        except Exception as e:
            logger.error(f"❌ SSL setup failed: {e}")
            return False

    def setup_load_balancer(self) -> bool:
        """Setup load balancer configuration"""
        logger.info("⚖️  Setting up load balancer...")

        if not self.config['load_balancer']['enabled']:
            logger.info("ℹ️  Load balancer setup skipped (disabled in config)")
            self.components['load_balancer'] = True
            return True

        try:
            # Generate nginx configuration
            nginx_config = f"""
upstream owlban_backend {{
    {"".join([f"    server {server};\\n" for server in self.config['load_balancer']['upstream_servers']])}
}}

server {{
    listen 80;
    server_name localhost;

    location / {{
        proxy_pass http://owlban_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    location /health {{
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}
}}
"""

            nginx_dir = self.project_root / 'nginx'
            nginx_dir.mkdir(exist_ok=True)

            with open(nginx_dir / 'nginx.conf', 'w') as f:
                f.write(nginx_config)

            self.components['load_balancer'] = True
            logger.info("✅ Load balancer setup completed")
            return True

        except Exception as e:
            logger.error(f"❌ Load balancer setup failed: {e}")
            return False

    def setup_monitoring(self) -> bool:
        """Setup monitoring stack"""
        logger.info("📊 Setting up monitoring...")

        if not self.config['monitoring']['enabled']:
            logger.info("ℹ️  Monitoring setup skipped (disabled in config)")
            self.components['monitoring'] = True
            return True

        try:
            # Create monitoring configuration
            monitoring_dir = self.project_root / 'monitoring'
            monitoring_dir.mkdir(exist_ok=True)

            # Prometheus configuration
            prometheus_config = f"""
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - localhost:{self.config['monitoring']['alertmanager_port']}

scrape_configs:
  - job_name: 'owlban'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
"""

            with open(monitoring_dir / 'prometheus.yml', 'w') as f:
                f.write(prometheus_config)

            # Alert rules
            alert_rules = """
groups:
  - name: owlban
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 5% for more than 5 minutes"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "Owlban service is not responding"
"""

            with open(monitoring_dir / 'alert_rules.yml', 'w') as f:
                f.write(alert_rules)

            self.components['monitoring'] = True
            logger.info("✅ Monitoring setup completed")
            return True

        except Exception as e:
            logger.error(f"❌ Monitoring setup failed: {e}")
            return False

    def setup_backup(self) -> bool:
        """Setup backup system"""
        logger.info("💾 Setting up backup system...")

        if not self.config['backup']['enabled']:
            logger.info("ℹ️  Backup setup skipped (disabled in config)")
            self.components['backup'] = True
            return True

        try:
            # Create backup script
            retention_days = self.config['backup']['retention_days']
            backup_script = f"""#!/bin/bash
# Automated backup script

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Database backup
echo "Backing up database..."
python database/migrations.py backup --backup-file "$BACKUP_DIR/database.sql"

# Application backup
echo "Backing up application..."
tar -czf "$BACKUP_DIR/app.tar.gz" \\
    --exclude='*.pyc' \\
    --exclude='__pycache__' \\
    --exclude='.git' \\
    --exclude='backups' \\
    --exclude='logs' \\
    .

# Configuration backup
echo "Backing up configuration..."
cp production_config.json "$BACKUP_DIR/" 2>/dev/null || true

echo "Backup completed: $BACKUP_DIR"

# Cleanup old backups
find backups -type d -mtime +{retention_days} -exec rm -rf {{}} + 2>/dev/null || true
"""

            with open('backup.sh', 'w') as f:
                f.write(backup_script)

            if not self.run_command("chmod +x backup.sh"):
                return False

            self.components['backup'] = True
            logger.info("✅ Backup setup completed")
            return True

        except Exception as e:
            logger.error(f"❌ Backup setup failed: {e}")
            return False

    def deploy_application(self) -> bool:
        """Deploy the application"""
        logger.info("🚀 Deploying application...")

        try:
            # Create docker-compose for production
            docker_compose = f"""
version: '3.8'

services:
  owlban-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL={self.config['database']['url']}
    depends_on:
      - postgres
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: owlban_db
      POSTGRES_USER: owlban
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - owlban-app
    restart: unless-stopped

volumes:
  postgres_data:
"""

            with open('docker-compose.prod.yml', 'w') as f:
                f.write(docker_compose)

            # Deploy based on configuration
            if self.config['deployment']['method'] == 'docker-compose':
                if not self.run_command("docker-compose -f docker-compose.prod.yml up -d"):
                    return False

            # Wait for health checks
            logger.info("⏳ Waiting for application to be healthy...")
            time.sleep(30)

            # Verify deployment
            if not self.run_command("curl -f http://localhost/health"):
                logger.warning("⚠️  Health check failed, but continuing...")

            self.components['deployment'] = True
            logger.info("✅ Application deployment completed")
            return True

        except Exception as e:
            logger.error(f"❌ Application deployment failed: {e}")
            return False

    def run_health_checks(self) -> bool:
        """Run comprehensive health checks"""
        logger.info("🏥 Running health checks...")

        checks = [
            ("Database connection", "python database/migrations.py test"),
            ("Application health", "curl -f http://localhost:8000/health"),
            ("Load balancer", "curl -f http://localhost/health"),
        ]

        failed_checks = []

        for check_name, check_command in checks:
            if not self.run_command(check_command):
                failed_checks.append(check_name)

        if failed_checks:
            logger.error(f"❌ Health checks failed: {', '.join(failed_checks)}")
            return False

        logger.info("✅ All health checks passed")
        return True

    def generate_report(self) -> str:
        """Generate deployment report"""
        report = f"""
# Production Deployment Report
Generated: {datetime.now().isoformat()}

## Configuration
{json.dumps(self.config, indent=2)}

## Component Status
"""

        for component, status in self.components.items():
            status_icon = "✅" if status else "❌"
            report += f"- {component}: {status_icon}\n"

        report += "\n## Next Steps\n"

        if all(self.components.values()):
            report += """
✅ All components deployed successfully!

Next steps:
1. Configure monitoring dashboards
2. Set up log aggregation
3. Configure backup schedules
4. Update DNS records
5. Perform security audit
"""
        else:
            failed_components = [k for k, v in self.components.items() if not v]
            report += f"""
❌ Some components failed to deploy: {', '.join(failed_components)}

Please check the logs and retry failed components.
"""

        return report

    def orchestrate_deployment(self) -> bool:
        """Orchestrate complete production deployment"""
        logger.info("🎯 Starting production orchestration...")

        steps = [
            ("Database Setup", self.setup_database),
            ("SSL Setup", self.setup_ssl),
            ("Load Balancer Setup", self.setup_load_balancer),
            ("Monitoring Setup", self.setup_monitoring),
            ("Backup Setup", self.setup_backup),
            ("Application Deployment", self.deploy_application),
            ("Health Checks", self.run_health_checks),
        ]

        for step_name, step_func in steps:
            logger.info(f"🔧 Executing: {step_name}")
            start_time = time.time()

            try:
                if not step_func():
                    logger.error(f"❌ Step failed: {step_name}")
                    return False

                duration = time.time() - start_time
                logger.info(f"✅ Completed: {step_name} ({duration:.1f}s)")

            except Exception as e:
                logger.error(f"❌ Step error in {step_name}: {e}")
                return False

        # Generate final report
        report = self.generate_report()
        with open('production_deployment_report.md', 'w') as f:
            f.write(report)

        logger.info("🎉 Production orchestration completed!")
        logger.info("📄 Report saved to: production_deployment_report.md")

        return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Production Orchestrator for OWLban')
    parser.add_argument('action', choices=[
        'deploy', 'database', 'ssl', 'load-balancer', 'monitoring',
        'backup', 'health-check', 'report'
    ], help='Action to perform')
    parser.add_argument('--config', default='production_config.json', help='Configuration file')
    parser.add_argument('--skip-health-checks', action='store_true', help='Skip health checks')

    args = parser.parse_args()

    orchestrator = ProductionOrchestrator(args.config)

    try:
        if args.action == 'deploy':
            success = orchestrator.orchestrate_deployment()

        elif args.action == 'database':
            success = orchestrator.setup_database()

        elif args.action == 'ssl':
            success = orchestrator.setup_ssl()

        elif args.action == 'load-balancer':
            success = orchestrator.setup_load_balancer()

        elif args.action == 'monitoring':
            success = orchestrator.setup_monitoring()

        elif args.action == 'backup':
            success = orchestrator.setup_backup()

        elif args.action == 'health-check':
            success = orchestrator.run_health_checks()

        elif args.action == 'report':
            report = orchestrator.generate_report()
            print(report)
            success = True

        if success:
            logger.info("✅ Operation completed successfully")
            sys.exit(0)
        else:
            logger.error("❌ Operation failed")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
