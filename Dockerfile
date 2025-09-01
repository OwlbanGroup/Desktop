# Multi-stage Docker build for OWLban Full Application

# Stage 1: Python Backend Builder
FROM python:3.11-slim as python-builder

WORKDIR /app

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python source code
COPY backend/ ./backend/
COPY organizational_leadership/ ./organizational_leadership/
COPY revenue_tracking.py nvidia_integration.py config.py ./

# Stage 2: Node.js Builder
FROM node:18-alpine as node-builder

WORKDIR /app

# Copy Node.js source and install dependencies
COPY OSCAR-BROOME-REVENUE/package*.json ./OSCAR-BROOME-REVENUE/
WORKDIR /app/OSCAR-BROOME-REVENUE
RUN npm ci --only=production

# Copy Node.js source code
COPY OSCAR-BROOME-REVENUE/ ./

# Build Node.js application if needed
RUN npm run build 2>/dev/null || echo "No build script found"

# Stage 3: Final Runtime Image
FROM python:3.11-slim

# Install Node.js runtime for the Node.js app
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy Python dependencies and code from python-builder
COPY --from=python-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-builder /app/backend ./backend
COPY --from=python-builder /app/organizational_leadership ./organizational_leadership
COPY --from=python-builder /app/revenue_tracking.py /app/nvidia_integration.py /app/config.py ./

# Copy Node.js application from node-builder
COPY --from=node-builder /app/OSCAR-BROOME-REVENUE ./OSCAR-BROOME-REVENUE

# Copy frontend static files
COPY frontend/ ./frontend/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Set environment variables
ENV PYTHONPATH=/app
ENV NODE_ENV=production
ENV FLASK_APP=backend/app_server.py
ENV OSCAR_BROOME_URL=http://localhost:4000

# Health check endpoint
RUN echo '{"status": "healthy"}' > /app/health.json

# Expose ports
EXPOSE 5000 4000

# Start both services
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
