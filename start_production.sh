#!/bin/bash
# Production start script

echo "Starting NVIDIA Control Panel API..."

# Activate virtual environment
source .venv/bin/activate

# Start with Gunicorn
gunicorn --config gunicorn.conf.py app_production:app

echo "Application started successfully"
