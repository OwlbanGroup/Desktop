#!/usr/bin/env python3
"""
Production Deployment Script for OWLban Group Integrated Application

This script automates the deployment process including:
- Building Docker images
- Deploying to Kubernetes cluster
- Running database migrations
- Starting monitoring and alerting services
- Verifying deployment status

Usage:
    python production_deploy.py deploy
    python production_deploy.py rollback
    python production_deploy.py status
"""

import subprocess
import sys
import logging

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
        sys.exit(result.returncode)
    return result

def build_docker_images():
    logging.info("Building Docker images...")
    run_command("docker build -t owlban-app:latest .")

def deploy_kubernetes():
    logging.info("Deploying to Kubernetes cluster...")
    run_command("kubectl apply -f k8s/")

def run_database_migrations():
    logging.info("Running database migrations...")
    run_command("python database/migrations.py")

def start_monitoring_services():
    logging.info("Starting monitoring and alerting services...")
    run_command("docker-compose -f monitoring/docker-compose.monitoring.yml up -d")

def check_deployment_status():
    logging.info("Checking deployment status...")
    run_command("kubectl rollout status deployment/owlban-app-deployment")

def rollback_deployment():
    logging.info("Rolling back deployment...")
    run_command("kubectl rollout undo deployment/owlban-app-deployment")

def main():
    if len(sys.argv) < 2:
        logging.error("No command provided. Use 'deploy', 'rollback', or 'status'.")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "deploy":
        build_docker_images()
        deploy_kubernetes()
        run_database_migrations()
        start_monitoring_services()
        check_deployment_status()
        logging.info("Deployment completed successfully.")
    elif command == "rollback":
        rollback_deployment()
        logging.info("Rollback completed successfully.")
    elif command == "status":
        check_deployment_status()
    else:
        logging.error(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
