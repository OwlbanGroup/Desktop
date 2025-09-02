#!/usr/bin/env python3
"""
Production Setup Script for Owlban Group Integrated Platform
Generates SSL certificates, NGINX configuration, and production-ready setup
"""

import os
import sys
import subprocess
from pathlib import Path

def create_ssl_certificates():
    """Generate SSL certificates for production"""
    print("🔒 Generating SSL certificates for production...")

    try:
        from ssl_config.ssl_manager import generate_ssl_cert

        # Create SSL directory if it doesn't exist
        ssl_dir = Path("./ssl")
        ssl_dir.mkdir(exist_ok=True)

        # Generate certificates
        certs = generate_ssl_cert(
            domain="api.owlban.group",
            cert_dir="./ssl"
        )

        print("✅ SSL certificates generated successfully:")
        print(f"   Certificate: {certs['certificate']}")
        print(f"   Private Key: {certs['private_key']}")

        return True

    except Exception as e:
        print(f"❌ Failed to generate SSL certificates: {e}")
        return False

def create_nginx_config():
    """Generate NGINX configuration for production"""
    print("⚖️ Generating NGINX load balancer configuration...")

    try:
        from load_balancer.nginx_config import create_production_config

        config_path = create_production_config()
        print(f"✅ NGINX configuration created: {config_path}")

        return True

    except Exception as e:
        print(f"❌ Failed to generate NGINX configuration: {e}")
        return False

def create_docker_compose_prod():
    """Create production Docker Compose configuration"""
    print("🐳 Creating production Docker Compose configuration...")

    docker_compose_prod = """
version: '3.8'

services:
  # Main application
  app:
    build: .
    ports:
      - "5000-5002:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@postgres:5432/owlban_db
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./ssl:/app/ssl:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL database
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=owlban_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d owlban_db"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis cache
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # NGINX load balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl/certs:ro
    depends_on:
      - app
    restart: unless-stopped

  # Monitoring - Prometheus
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  # Monitoring - Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  grafana_data:

networks:
  default:
    driver: bridge
"""

    with open("docker-compose.prod.yml", "w") as f:
        f.write(docker_compose_prod.strip())

    print("✅ Production Docker Compose configuration created: docker-compose.prod.yml")
    return True

def create_deployment_script():
    """Create deployment script"""
    print("🚀 Creating deployment script...")

    deploy_script = """#!/bin/bash
# Production Deployment Script for Owlban Group Platform

set -e

echo "🚀 Starting production deployment..."

# Check if required tools are installed
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting."; exit 1; }

# Generate SSL certificates if they don't exist
if [ ! -f "./ssl/server.crt" ]; then
    echo "🔒 Generating SSL certificates..."
    python3 -c "from production_setup import create_ssl_certificates; create_ssl_certificates()"
fi

# Generate NGINX configuration if it doesn't exist
if [ ! -f "./nginx.prod.conf" ]; then
    echo "⚖️ Generating NGINX configuration..."
    python3 -c "from production_setup import create_nginx_config; create_nginx_config()"
fi

# Create production Docker Compose if it doesn't exist
if [ ! -f "./docker-compose.prod.yml" ]; then
    echo "🐳 Creating production Docker Compose..."
    python3 -c "from production_setup import create_docker_compose_prod; create_docker_compose_prod()"
fi

# Set environment variables
export JWT_SECRET_KEY="${JWT_SECRET_KEY:-$(openssl rand -hex 32)}"

# Build and start services
echo "🐳 Building and starting production services..."
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
curl -f http://localhost/health || echo "⚠️ Health check failed - services may still be starting"

echo "✅ Production deployment completed!"
echo ""
echo "🌐 Services available at:"
echo "   Main Application: http://localhost"
echo "   SSL Application: https://localhost"
echo "   Grafana: http://localhost:3000 (admin/admin)"
echo "   Prometheus: http://localhost:9090"
echo ""
echo "📊 To view logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "🛑 To stop: docker-compose -f docker-compose.prod.yml down"
"""

    with open("deploy.sh", "w") as f:
        f.write(deploy_script)

    # Make script executable
    os.chmod("deploy.sh", 0o755)

    print("✅ Deployment script created: deploy.sh")
    return True

def main():
    """Main setup function"""
    print("🦉 Owlban Group Integrated Platform - Production Setup")
    print("=" * 60)

    success_count = 0
    total_steps = 4

    # Step 1: SSL Certificates
    if create_ssl_certificates():
        success_count += 1

    # Step 2: NGINX Configuration
    if create_nginx_config():
        success_count += 1

    # Step 3: Docker Compose Production
    if create_docker_compose_prod():
        success_count += 1

    # Step 4: Deployment Script
    if create_deployment_script():
        success_count += 1

    print("\n" + "=" * 60)
    print(f"📊 Setup completed: {success_count}/{total_steps} steps successful")

    if success_count == total_steps:
        print("✅ Production setup completed successfully!")
        print("\n🚀 To deploy: ./deploy.sh")
    else:
        print("⚠️ Some steps failed. Please check the errors above.")

    return success_count == total_steps

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
