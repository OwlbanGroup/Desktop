#!/bin/bash
# Production stop script

echo "Stopping NVIDIA Control Panel API..."

# Kill Gunicorn processes
pkill -f gunicorn

echo "Application stopped"
