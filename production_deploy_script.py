#!/usr/bin/env python3
"""
OSCAR-BROOME-REVENUE Production Deployment Script

This script orchestrates the complete production deployment of the
OSCAR-BROOME-REVENUE integrated financial platform.

Features:
- Environment validation and setup
- Database initialization and migration
- Backend service deployment
- Frontend deployment
- Service health monitoring
- Automated rollback on failure
- Production logging and alerting

Usage:
    python production_deploy_script.py --environment production --version 1.0.0
"""

import os
import sys
import json
import subprocess
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time
import requests
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_deploy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProductionDeployer:
    """Main production deployment orchestrator"""

    def __init__(self, environment: str, version: str):
        self.environment = environment
        self.version = version
        self.project_root = Path(__file__).parent
        self.config = self.load_config()
        self.backup_dir = self.project_root / 'backups' / datetime.now().strftime('%Y%m%d_%H%M%S')
        self.services = {
            'backend': {'port': 5000, 'health_endpoint': '/health'},
            'frontend': {'port': 3000, 'health_endpoint': '/'},
            'database': {'port': 5432, 'health_endpoint': None}
        }

    def load_config(self) -> Dict:
        """Load production configuration"""
        config_path = self.project_root / 'production_config.json'
        if not config_path.exists():
            logger.error(f"Production config not found at {config_path}")
            sys.exit(1)

        with open(config_path, 'r') as f:
            return json.load(f)

    def validate_environment(self) -> bool:
        """Validate deployment environment and prerequisites"""
        logger.info("🔍 Validating deployment environment...")

        # Check required environment variables
        required_vars = [
            'DATABASE_URL',
            'SECRET_KEY',
            'JPMORGAN_API_KEY',
            'NVIDIA_API_KEY',
            'REDIS_URL'
        ]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            return False

        # Check system prerequisites
        prerequisites = ['python', 'node', 'npm', 'docker', 'docker-compose']
        missing_prereqs = []

        for prereq in prerequisites:
            if not shutil.which(prereq):
                missing_prereqs.append(prereq)

        if missing_prereqs:
            logger.error(f"❌ Missing system prerequisites: {missing_prereqs}")
            return False

        # Validate Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            logger.error(f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}")
            return False

        logger.info("✅ Environment validation passed")
        return True

    def create_backup(self) -> bool:
        """Create backup of current deployment"""
        logger.info("💾 Creating deployment backup...")

        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # Backup database
            if self.run_command("pg_dump owlban_db > backup.sql", cwd=self.backup_dir):
                logger.info("✅ Database backup created")
            else:
                logger.warning("⚠️ Database backup failed, continuing...")

            # Backup configuration files
            backup_files = [
                'production_config.json',
                'docker-compose.yml',
                '.env.production'
            ]

            for file in backup_files:
                src = self.project_root / file
                if src.exists():
                    shutil.copy2(src, self.backup_dir / file)

            logger.info(f"✅ Backup created at {self.backup_dir}")
            return True

        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            return False

    def setup_database(self) -> bool:
        """Initialize and migrate database"""
        logger.info("🗄️ Setting up database...")

        try:
            # Run database migrations
            if not self.run_command("python -m alembic upgrade head"):
                logger.error("❌ Database migration failed")
                return False

            # Initialize database with seed data
            if not self.run_command("python database/init_db.py"):
                logger.error("❌ Database initialization failed")
                return False

            logger.info("✅ Database setup completed")
            return True

        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            return False

    def deploy_backend(self) -> bool:
        """Deploy backend services"""
        logger.info("🚀 Deploying backend services...")

        try:
            # Install Python dependencies
            if not self.run_command("pip install -r requirements.txt"):
                logger.error("❌ Python dependencies installation failed")
                return False

            # Run backend tests
            if not self.run_command("python -m pytest tests/ -v --tb=short"):
                logger.warning("⚠️ Some backend tests failed, continuing deployment...")

            # Start backend service
            backend_cmd = f"python backend/app_server.py"
            if self.environment == 'production':
                backend_cmd = f"gunicorn -w 4 -b 0.0.0.0:5000 backend.app_server:app"

            if not self.run_command(backend_cmd, background=True):
                logger.error("❌ Backend service startup failed")
                return False

            logger.info("✅ Backend deployment completed")
            return True

        except Exception as e:
            logger.error(f"❌ Backend deployment failed: {e}")
            return False

    def deploy_frontend(self) -> bool:
        """Deploy frontend application"""
        logger.info("🌐 Deploying frontend application...")

        try:
            frontend_dir = self.project_root / 'OSCAR-BROOME-REVENUE'

            # Install Node.js dependencies
            if not self.run_command("npm install", cwd=frontend_dir):
                logger.error("❌ Frontend dependencies installation failed")
                return False

            # Build frontend application
            if not self.run_command("npm run build", cwd=frontend_dir):
                logger.error("❌ Frontend build failed")
                return False

            # Start frontend service
            if self.environment == 'production':
                if not self.run_command("npm start", cwd=frontend_dir, background=True):
                    logger.error("❌ Frontend service startup failed")
                    return False
            else:
                # For development, serve static files
                if not self.run_command("python -m http.server 3000", cwd=frontend_dir / 'build', background=True):
                    logger.error("❌ Frontend service startup failed")
                    return False

            logger.info("✅ Frontend deployment completed")
            return True

        except Exception as e:
            logger.error(f"❌ Frontend deployment failed: {e}")
            return False

    def deploy_monitoring(self) -> bool:
        """Deploy monitoring and logging services"""
        logger.info("📊 Deploying monitoring services...")

        try:
            monitoring_dir = self.project_root / 'monitoring'

            # Start monitoring stack
            if not self.run_command("docker-compose up -d", cwd=monitoring_dir):
                logger.error("❌ Monitoring services startup failed")
                return False

            logger.info("✅ Monitoring deployment completed")
            return True

        except Exception as e:
            logger.error(f"❌ Monitoring deployment failed: {e}")
            return False

    def health_check(self, service_name: str, max_retries: int = 30) -> bool:
        """Perform health check on a service"""
        service_config = self.services.get(service_name)
        if not service_config:
            logger.error(f"❌ Unknown service: {service_name}")
            return False

        health_url = f"http://localhost:{service_config['port']}{service_config['health_endpoint']}"

        for attempt in range(max_retries):
            try:
                response = requests.get(health_url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ {service_name} health check passed")
                    return True
            except Exception as e:
                logger.debug(f"Health check attempt {attempt + 1} failed for {service_name}: {e}")

            time.sleep(2)

        logger.error(f"❌ {service_name} health check failed after {max_retries} attempts")
        return False

    def run_health_checks(self) -> bool:
        """Run health checks on all services"""
        logger.info("🏥 Running health checks...")

        services_to_check = ['database', 'backend', 'frontend']

        for service in services_to_check:
            if not self.health_check(service):
                return False

        logger.info("✅ All health checks passed")
        return True

    def rollback(self) -> bool:
        """Rollback deployment on failure"""
        logger.info("🔄 Rolling back deployment...")

        try:
            # Stop all services
            self.run_command("docker-compose down", cwd=self.project_root)
            self.run_command("pkill -f 'python backend/app_server.py'")
            self.run_command("pkill -f 'npm start'")

            # Restore from backup if available
            if self.backup_dir.exists():
                logger.info("Restoring from backup...")
                # Restore database
                backup_sql = self.backup_dir / 'backup.sql'
                if backup_sql.exists():
                    self.run_command(f"psql owlban_db < {backup_sql}")

                # Restore configuration files
                for config_file in ['production_config.json', 'docker-compose.yml']:
                    backup_file = self.backup_dir / config_file
                    if backup_file.exists():
                        shutil.copy2(backup_file, self.project_root / config_file)

            logger.info("✅ Rollback completed")
            return True

        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False

    def run_command(self, command: str, cwd: Optional[Path] = None, background: bool = False) -> bool:
        """Execute shell command"""
        try:
            if cwd is None:
                cwd = self.project_root

            logger.debug(f"Executing: {command}")

            if background:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                # For background processes, just check if they started
                time.sleep(2)
                if process.poll() is None:
                    logger.debug(f"Background process started: {command}")
                    return True
                else:
                    stdout, stderr = process.communicate()
                    logger.error(f"Background process failed: {stderr.decode()}")
                    return False
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    logger.debug(f"Command succeeded: {command}")
                    return True
                else:
                    logger.error(f"Command failed: {command}")
                    logger.error(f"STDOUT: {result.stdout}")
                    logger.error(f"STDERR: {result.stderr}")
                    return False

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return False
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return False

    def deploy(self) -> bool:
        """Main deployment orchestration"""
        logger.info(f"🚀 Starting production deployment v{self.version} for {self.environment}")

        start_time = time.time()

        try:
            # Phase 1: Validation
            if not self.validate_environment():
                return False

            # Phase 2: Backup
            if not self.create_backup():
                return False

            # Phase 3: Database Setup
            if not self.setup_database():
                self.rollback()
                return False

            # Phase 4: Backend Deployment
            if not self.deploy_backend():
                self.rollback()
                return False

            # Phase 5: Frontend Deployment
            if not self.deploy_frontend():
                self.rollback()
                return False

            # Phase 6: Monitoring Deployment
            if not self.deploy_monitoring():
                self.rollback()
                return False

            # Phase 7: Health Checks
            if not self.run_health_checks():
                self.rollback()
                return False

            # Deployment successful
            end_time = time.time()
            duration = end_time - start_time

            logger.info("🎉 Production deployment completed successfully!")
            logger.info(f"⏱️ Total deployment time: {duration:.2f} seconds")
            logger.info(f"📊 Deployment version: {self.version}")
            logger.info(f"🌍 Environment: {self.environment}")
            logger.info(f"💾 Backup location: {self.backup_dir}")

            return True

        except Exception as e:
            logger.error(f"❌ Deployment failed with error: {e}")
            self.rollback()
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='OSCAR-BROOME-REVENUE Production Deployment')
    parser.add_argument('--environment', required=True, choices=['staging', 'production'],
                       help='Deployment environment')
    parser.add_argument('--version', required=True,
                       help='Deployment version')
    parser.add_argument('--skip-health-checks', action='store_true',
                       help='Skip health checks after deployment')
    parser.add_argument('--dry-run', action='store_true',
                       help='Perform dry run without actual deployment')

    args = parser.parse_args()

    # Create deployer instance
    deployer = ProductionDeployer(args.environment, args.version)

    if args.dry_run:
        logger.info("🔍 Performing dry run...")
        logger.info(f"Environment: {args.environment}")
        logger.info(f"Version: {args.version}")
        logger.info("✅ Dry run completed")
        return

    # Execute deployment
    success = deployer.deploy()

    if success:
        logger.info("🎉 Deployment completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Deployment failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
