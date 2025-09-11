#!/usr/bin/env python3
"""
Environment Setup Script for OWLban Group Integrated Application

This script handles complete environment setup including:
- Dependency installation
- Environment configuration
- Database initialization
- Service configuration
- Security setup

Usage:
    python environment_setup.py install
    python environment_setup.py configure
    python environment_setup.py initialize
    python environment_setup.py verify
"""

import subprocess
import sys
import logging
import json
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def run_command(command, check=True):
    logging.info(f"Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        logging.info(f"Output: {result.stdout.strip()}")
    if result.stderr:
        logging.error(f"Error: {result.stderr.strip()}")
    if check and result.returncode != 0:
        logging.error(f"Command failed with exit code {result.returncode}")
        return False
    return True

def install_dependencies():
    logging.info("Installing Python dependencies...")
    if run_command("pip install -r requirements-dev.txt"):
        logging.info("✅ Python dependencies installed successfully")
        return True
    else:
        logging.error("❌ Failed to install Python dependencies")
        return False

def install_nodejs_dependencies():
    logging.info("Installing Node.js dependencies...")
    if os.path.exists("OSCAR-BROOME-REVENUE/package.json"):
        os.chdir("OSCAR-BROOME-REVENUE")
        if run_command("npm install"):
            logging.info("✅ Node.js dependencies installed successfully")
            os.chdir("..")
            return True
        else:
            logging.error("❌ Failed to install Node.js dependencies")
            os.chdir("..")
            return False
    else:
        logging.warning("⚠️  No package.json found, skipping Node.js dependencies")
        return True

def setup_database():
    logging.info("Setting up database...")
    if run_command("python database/init_db.py"):
        logging.info("✅ Database initialized successfully")
        return True
    else:
        logging.error("❌ Failed to initialize database")
        return False

def configure_environment():
    logging.info("Configuring environment variables...")

    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        env_template = """
# Database Configuration
DATABASE_URL=sqlite:///owlban.db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=owlban_db
DB_USER=owlban_user
DB_PASSWORD=secure_password

# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# API Keys (Configure these with actual values)
OPENWEATHER_API_KEY=your-openweather-api-key
JPMORGAN_API_KEY=your-jpmorgan-api-key
CHASE_API_KEY=your-chase-api-key
NVIDIA_API_KEY=your-nvidia-api-key

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-email-password

# Security Configuration
JWT_SECRET_KEY=your-jwt-secret-key
ENCRYPTION_KEY=your-encryption-key

# Monitoring Configuration
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
"""
        with open(env_file, 'w') as f:
            f.write(env_template.strip())
        logging.info("✅ Created .env file with default configuration")
    else:
        logging.info("✅ .env file already exists")

    return True

def setup_ssl_certificates():
    logging.info("Setting up SSL certificates...")
    ssl_dir = Path("ssl_config")
    ssl_dir.mkdir(exist_ok=True)

    # Generate self-signed certificate for development
    if run_command("openssl req -x509 -newkey rsa:4096 -keyout ssl_config/key.pem -out ssl_config/cert.pem -days 365 -nodes -subj '/C=US/ST=State/L=City/O=Organization/CN=localhost'"):
        logging.info("✅ SSL certificates generated successfully")
        return True
    else:
        logging.error("❌ Failed to generate SSL certificates")
        return False

def configure_nginx():
    logging.info("Configuring Nginx...")
    nginx_config = """
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/static/files;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

server {
    listen 443 ssl;
    server_name localhost;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""
    with open("nginx.conf", 'w') as f:
        f.write(nginx_config.strip())
    logging.info("✅ Nginx configuration created")
    return True

def setup_monitoring():
    logging.info("Setting up monitoring services...")
    monitoring_dir = Path("monitoring")
    monitoring_dir.mkdir(exist_ok=True)

    # Create Prometheus configuration
    prometheus_config = """
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'owlban-app'
    static_configs:
      - targets: ['localhost:5000']
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
"""
    with open("monitoring/prometheus.yml", 'w') as f:
        f.write(prometheus_config.strip())

    logging.info("✅ Monitoring configuration created")
    return True

def initialize_services():
    logging.info("Initializing services...")

    # Create necessary directories
    directories = [
        "logs",
        "backups",
        "uploads",
        "cache",
        "temp"
    ]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logging.info(f"✅ Created directory: {directory}")

    # Set proper permissions
    if run_command("chmod -R 755 logs backups uploads cache temp"):
        logging.info("✅ Set proper permissions on directories")
    else:
        logging.warning("⚠️  Could not set directory permissions (may not be applicable on Windows)")

    return True

def verify_setup():
    logging.info("Verifying environment setup...")

    checks = [
        ("Python dependencies", "python -c 'import flask, sqlalchemy, redis'"),
        ("Database connection", "python -c 'from database.connection import get_db; get_db()'"),
        ("Environment variables", "python -c 'import os; print(os.getenv(\"FLASK_APP\"))'"),
        ("SSL certificates", "ls ssl_config/"),
        ("Nginx config", "ls nginx.conf"),
        ("Monitoring config", "ls monitoring/")
    ]

    passed = 0
    total = len(checks)

    for check_name, command in checks:
        if run_command(command, check=False):
            logging.info(f"✅ {check_name}: OK")
            passed += 1
        else:
            logging.error(f"❌ {check_name}: FAILED")

    logging.info(f"Verification complete: {passed}/{total} checks passed")

    if passed == total:
        logging.info("🎉 Environment setup verification successful!")
        return True
    else:
        logging.warning("⚠️  Some checks failed. Please review the setup.")
        return False

def main():
    if len(sys.argv) < 2:
        logging.error("No command provided. Use 'install', 'configure', 'initialize', or 'verify'.")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "install":
        success = install_dependencies() and install_nodejs_dependencies()
        if success:
            logging.info("✅ Installation completed successfully")
        else:
            logging.error("❌ Installation failed")
            sys.exit(1)

    elif command == "configure":
        success = configure_environment() and setup_ssl_certificates() and configure_nginx() and setup_monitoring()
        if success:
            logging.info("✅ Configuration completed successfully")
        else:
            logging.error("❌ Configuration failed")
            sys.exit(1)

    elif command == "initialize":
        success = setup_database() and initialize_services()
        if success:
            logging.info("✅ Initialization completed successfully")
        else:
            logging.error("❌ Initialization failed")
            sys.exit(1)

    elif command == "verify":
        if verify_setup():
            logging.info("✅ Environment setup is valid")
        else:
            logging.error("❌ Environment setup has issues")
            sys.exit(1)

    else:
        logging.error(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
