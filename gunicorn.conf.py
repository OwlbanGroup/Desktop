
# Gunicorn configuration for production
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = "info"
accesslog = "logs/access.log"
errorlog = "logs/error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "nvidia-control-panel-api"

# Server mechanics
preload_app = True
pidfile = "logs/gunicorn.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None
