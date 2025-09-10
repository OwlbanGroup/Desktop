#!/usr/bin/env python3
"""
Production Deployment Setup for Chase Integration
Sets up production-ready deployment with Docker, monitoring, and security
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
import yaml

class ChaseProductionDeployment:
    """Production deployment setup for Chase integration"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.docker_compose_file = self.project_root / "docker-compose.prod.yml"
        self.nginx_config_file = self.project_root / "nginx.prod.conf"
        self.env_file = self.project_root / ".env.prod"
        self.ssl_dir = self.project_root / "ssl"

    def create_docker_compose_prod(self):
        """Create production Docker Compose configuration"""
        docker_compose_config = {
            'version': '3.8',
            'services': {
                'chase-app': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'Dockerfile.prod'
                    },
                    'container_name': 'chase-integration-prod',
                    'restart': 'unless-stopped',
                    'ports': ['443:443', '80:80'],
                    'environment': [
                        'FLASK_ENV=production',
                        'FLASK_DEBUG=false',
                        'SECRET_KEY=${SECRET_KEY}',
                        'CHASE_API_KEY=${CHASE_API_KEY}',
                        'DATABASE_URL=${DATABASE_URL}',
                        'REDIS_URL=${REDIS_URL}'
                    ],
                    'volumes': [
                        './logs:/app/logs',
                        './ssl:/app/ssl:ro',
                        './data:/app/data'
                    ],
                    'depends_on': ['redis', 'postgres'],
                    'networks': ['chase-network']
                },
                'postgres': {
                    'image': 'postgres:15-alpine',
                    'container_name': 'chase-postgres-prod',
                    'restart': 'unless-stopped',
                    'environment': [
                        'POSTGRES_DB=chase_prod',
                        'POSTGRES_USER=${DB_USER}',
                        'POSTGRES_PASSWORD=${DB_PASSWORD}'
                    ],
                    'volumes': [
                        'postgres_data:/var/lib/postgresql/data',
                        './init.sql:/docker-entrypoint-initdb.d/init.sql'
                    ],
                    'networks': ['chase-network']
                },
                'redis': {
                    'image': 'redis:7-alpine',
                    'container_name': 'chase-redis-prod',
                    'restart': 'unless-stopped',
                    'command': 'redis-server --appendonly yes',
                    'volumes': ['redis_data:/data'],
                    'networks': ['chase-network']
                },
                'nginx': {
                    'image': 'nginx:alpine',
                    'container_name': 'chase-nginx-prod',
                    'restart': 'unless-stopped',
                    'ports': ['80:80', '443:443'],
                    'volumes': [
                        './nginx.prod.conf:/etc/nginx/nginx.conf:ro',
                        './ssl:/etc/ssl/certs:ro',
                        './static:/var/www/static:ro'
                    ],
                    'depends_on': ['chase-app'],
                    'networks': ['chase-network']
                },
                'prometheus': {
                    'image': 'prom/prometheus:latest',
                    'container_name': 'chase-prometheus-prod',
                    'restart': 'unless-stopped',
                    'ports': ['9090:9090'],
                    'volumes': [
                        './monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro',
                        'prometheus_data:/prometheus'
                    ],
                    'command': [
                        '--config.file=/etc/prometheus/prometheus.yml',
                        '--storage.tsdb.path=/prometheus',
                        '--web.console.libraries=/etc/prometheus/console_libraries',
                        '--web.console.templates=/etc/prometheus/consoles',
                        '--storage.tsdb.retention.time=200h',
                        '--web.enable-lifecycle'
                    ],
                    'networks': ['chase-network']
                },
                'grafana': {
                    'image': 'grafana/grafana:latest',
                    'container_name': 'chase-grafana-prod',
                    'restart': 'unless-stopped',
                    'ports': ['3000:3000'],
                    'environment': [
                        'GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}',
                        'GF_USERS_ALLOW_SIGN_UP=false'
                    ],
                    'volumes': [
                        'grafana_data:/var/lib/grafana',
                        './monitoring/grafana/provisioning:/etc/grafana/provisioning:ro'
                    ],
                    'depends_on': ['prometheus'],
                    'networks': ['chase-network']
                }
            },
            'volumes': {
                'postgres_data': {'driver': 'local'},
                'redis_data': {'driver': 'local'},
                'prometheus_data': {'driver': 'local'},
                'grafana_data': {'driver': 'local'}
            },
            'networks': {
                'chase-network': {
                    'driver': 'bridge'
                }
            }
        }

        with open(self.docker_compose_file, 'w') as f:
            yaml.dump(docker_compose_config, f, default_flow_style=False)

        print("✅ Created production Docker Compose configuration")

