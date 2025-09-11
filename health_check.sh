#!/bin/bash
# Health check script

HEALTH_URL="http://localhost:8000/health"
TIMEOUT=10

response=$(curl -s -w "%{http_code}" -o /dev/null --max-time $TIMEOUT $HEALTH_URL)
exit_code=$?

if [ $exit_code -eq 0 ] && [ "$response" = "200" ]; then
    echo "[SUCCESS] Application is healthy"
    exit 0
else
    echo "[ERROR] Application is unhealthy (HTTP $response)"
    exit 1
fi
