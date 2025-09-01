#!/bin/bash
set -e

# Function to start Node.js server
start_nodejs() {
    echo "Starting Node.js server..."
    cd /app/OSCAR-BROOME-REVENUE
    node server-enhanced.js &
    NODEJS_PID=$!
    echo "Node.js server started with PID: $NODEJS_PID"
}

# Function to start Python Flask server
start_python() {
    echo "Starting Python Flask server..."
    cd /app
    python -m flask run --host=0.0.0.0 --port=5000 &
    PYTHON_PID=$!
    echo "Python Flask server started with PID: $PYTHON_PID"
}

# Function to handle shutdown
shutdown() {
    echo "Shutting down services..."
    if [ ! -z "$NODEJS_PID" ]; then
        kill $NODEJS_PID || true
    fi
    if [ ! -z "$PYTHON_PID" ]; then
        kill $PYTHON_PID || true
    fi
    exit 0
}

# Set up signal handlers
trap shutdown SIGTERM SIGINT

# Start services
start_nodejs
start_python

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 5

# Health check
echo "Performing health checks..."
if curl -f http://localhost:4000/health 2>/dev/null; then
    echo "Node.js server is healthy"
else
    echo "Node.js server health check failed"
fi

if curl -f http://localhost:5000/health 2>/dev/null; then
    echo "Python Flask server is healthy"
else
    echo "Python Flask server health check failed"
fi

echo "Both services are running!"
echo "Node.js server: http://localhost:4000"
echo "Python Flask server: http://localhost:5000"

# Keep container running
wait
