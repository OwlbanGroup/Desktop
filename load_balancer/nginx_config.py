"""
NGINX load balancer configuration generator
"""

from typing import List, Dict, Any, Optional
import os

class NginxLoadBalancer:
    """
    NGINX load balancer configuration generator
    """

    def __init__(self, upstream_servers: List[str], domain: str = "localhost"):
        """
        Initialize load balancer configuration

        Args:
            upstream_servers: List of backend server URLs (e.g., ['http://localhost:5000', 'http://localhost:5001'])
            domain: Domain name for the load balancer
        """
        self.upstream_servers = upstream_servers
        self.domain = domain
        self.ssl_enabled = False
        self.ssl_cert_path = ""
        self.ssl_key_path = ""

    def enable_ssl(self, cert_path: str, key_path: str):
        """
        Enable SSL/TLS for the load balancer

        Args:
            cert_path: Path to SSL certificate
            key_path: Path to SSL private key
        """
        self.ssl_enabled = True
        self.ssl_cert_path = cert_path
        self.ssl_key_path = key_path

    def generate_upstream_config(self) -> str:
        """
        Generate upstream server configuration

        Returns:
            NGINX upstream configuration block
        """
        upstream_config = "upstream owlban_backend {\n"
        upstream_config += "    least_conn;\n"  # Least connections load balancing

        for i, server in enumerate(self.upstream_servers):
            upstream_config += f"    server {server} weight=1 max_fails=3 fail_timeout=30s;\n"

        upstream_config += "}\n\n"
        return upstream_config

    def generate_server_config(self) -> str:
        """
        Generate server configuration

        Returns:
            NGINX server configuration block
        """
        server_config = f"server {{\n"
        server_config += f"    listen 80{' ssl' if self.ssl_enabled else ''};\n"

        if self.ssl_enabled:
            server_config += f"    ssl_certificate {self.ssl_cert_path};\n"
            server_config += f"    ssl_certificate_key {self.ssl_key_path};\n"
            server_config += "    ssl_protocols TLSv1.2 TLSv1.3;\n"
            server_config += "    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;\n"
            server_config += "    ssl_prefer_server_ciphers off;\n"

        server_config += f"    server_name {self.domain};\n\n"

        # Security headers
        server_config += "    # Security headers\n"
        server_config += "    add_header X-Frame-Options DENY;\n"
        server_config += "    add_header X-Content-Type-Options nosniff;\n"
        server_config += "    add_header X-XSS-Protection '1; mode=block';\n"
        server_config += "    add_header Strict-Transport-Security 'max-age=31536000; includeSubDomains' always;\n"
        server_config += "    add_header Referrer-Policy 'strict-origin-when-cross-origin';\n\n"

        # Rate limiting
        server_config += "    # Rate limiting\n"
        server_config += "    limit_req zone=api burst=10 nodelay;\n"
        server_config += "    limit_req zone=auth burst=5 nodelay;\n\n"

        # Static file serving
        server_config += "    # Static file serving\n"
        server_config += "    location /static/ {\n"
        server_config += "        proxy_pass http://owlban_backend/static/;\n"
        server_config += "        expires 1y;\n"
        server_config += "        add_header Cache-Control 'public, immutable';\n"
        server_config += "    }\n\n"

        # API endpoints
        server_config += "    # API endpoints\n"
        server_config += "    location /api/ {\n"
        server_config += "        proxy_pass http://owlban_backend;\n"
        server_config += "        proxy_set_header Host $host;\n"
        server_config += "        proxy_set_header X-Real-IP $remote_addr;\n"
        server_config += "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
        server_config += "        proxy_set_header X-Forwarded-Proto $scheme;\n"
        server_config += "        proxy_connect_timeout 30s;\n"
        server_config += "        proxy_send_timeout 30s;\n"
        server_config += "        proxy_read_timeout 30s;\n"
        server_config += "    }\n\n"

        # WebSocket support
        server_config += "    # WebSocket support\n"
        server_config += "    location /socket.io/ {\n"
        server_config += "        proxy_pass http://owlban_backend;\n"
        server_config += "        proxy_http_version 1.1;\n"
        server_config += "        proxy_set_header Upgrade $http_upgrade;\n"
        server_config += "        proxy_set_header Connection 'upgrade';\n"
        server_config += "        proxy_set_header Host $host;\n"
        server_config += "        proxy_set_header X-Real-IP $remote_addr;\n"
        server_config += "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
        server_config += "        proxy_set_header X-Forwarded-Proto $scheme;\n"
        server_config += "        proxy_connect_timeout 7d;\n"
        server_config += "        proxy_send_timeout 7d;\n"
        server_config += "        proxy_read_timeout 7d;\n"
        server_config += "    }\n\n"

        # Frontend serving
        server_config += "    # Frontend serving\n"
        server_config += "    location / {\n"
        server_config += "        proxy_pass http://owlban_backend;\n"
        server_config += "        proxy_set_header Host $host;\n"
        server_config += "        proxy_set_header X-Real-IP $remote_addr;\n"
        server_config += "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
        server_config += "        proxy_set_header X-Forwarded-Proto $scheme;\n"
        server_config += "        proxy_connect_timeout 30s;\n"
        server_config += "        proxy_send_timeout 30s;\n"
        server_config += "        proxy_read_timeout 30s;\n"
        server_config += "    }\n\n"

        # Health check endpoint
        server_config += "    # Health check\n"
        server_config += "    location /health {\n"
        server_config += "        access_log off;\n"
        server_config += "        return 200 'healthy\\n';\n"
        server_config += "        add_header Content-Type text/plain;\n"
        server_config += "    }\n\n"

        server_config += "}\n\n"
        return server_config

    def generate_rate_limiting_config(self) -> str:
        """
        Generate rate limiting configuration

        Returns:
            NGINX rate limiting configuration
        """
        rate_limit_config = "# Rate limiting zones\n"
        rate_limit_config += "limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;\n"
        rate_limit_config += "limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;\n"
        rate_limit_config += "limit_req_zone $binary_remote_addr zone=static:10m rate=100r/s;\n\n"
        return rate_limit_config

    def generate_full_config(self) -> str:
        """
        Generate complete NGINX configuration

        Returns:
            Complete NGINX configuration
        """
        config = "# Owlban Group Load Balancer Configuration\n"
        config += "# Generated automatically - do not edit manually\n\n"

        # Events block
        config += "events {\n"
        config += "    worker_connections 1024;\n"
        config += "}\n\n"

        # HTTP block
        config += "http {\n"
        config += "    include /etc/nginx/mime.types;\n"
        config += "    default_type application/octet-stream;\n\n"

        # Logging
        config += "    # Logging\n"
        config += "    log_format main '$remote_addr - $remote_user [$time_local] \"$request\" '\n"
        config += "                      '$status $body_bytes_sent \"$http_referer\" '\n"
        config += "                      '\"$http_user_agent\" \"$http_x_forwarded_for\"';\n\n"
        config += "    access_log /var/log/nginx/access.log main;\n"
        config += "    error_log /var/log/nginx/error.log;\n\n"

        # Performance optimizations
        config += "    # Performance optimizations\n"
        config += "    sendfile on;\n"
        config += "    tcp_nopush on;\n"
        config += "    tcp_nodelay on;\n"
        config += "    keepalive_timeout 65;\n"
        config += "    types_hash_max_size 2048;\n"
        config += "    client_max_body_size 100M;\n\n"

        # Gzip compression
        config += "    # Gzip compression\n"
        config += "    gzip on;\n"
        config += "    gzip_vary on;\n"
        config += "    gzip_min_length 1024;\n"
        config += "    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;\n\n"

        # Rate limiting
        config += self.generate_rate_limiting_config()

        # Upstream servers
        config += self.generate_upstream_config()

        # Server configuration
        config += self.generate_server_config()

        config += "}\n"
        return config

    def save_config(self, filepath: str):
        """
        Save configuration to file

        Args:
            filepath: Path to save the configuration file
        """
        config = self.generate_full_config()

        with open(filepath, 'w') as f:
            f.write(config)

        print(f"✅ NGINX configuration saved to {filepath}")

def generate_nginx_config(upstream_servers: List[str], domain: str = "localhost",
                         output_path: str = "/etc/nginx/nginx.conf",
                         ssl_cert: Optional[str] = None, ssl_key: Optional[str] = None) -> str:
    """
    Generate and optionally save NGINX load balancer configuration

    Args:
        upstream_servers: List of backend server URLs
        domain: Domain name for the load balancer
        output_path: Path to save the configuration (optional)
        ssl_cert: Path to SSL certificate (optional)
        ssl_key: Path to SSL private key (optional)

    Returns:
        Generated NGINX configuration
    """
    lb = NginxLoadBalancer(upstream_servers, domain)

    if ssl_cert and ssl_key:
        lb.enable_ssl(ssl_cert, ssl_key)

    config = lb.generate_full_config()

    if output_path:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        lb.save_config(output_path)

    return config

# Example usage and configuration templates
def create_development_config():
    """Create development environment configuration"""
    return generate_nginx_config(
        upstream_servers=['http://localhost:5000', 'http://localhost:5001'],
        domain='localhost',
        output_path='./nginx.dev.conf'
    )

def create_production_config():
    """Create production environment configuration"""
    return generate_nginx_config(
        upstream_servers=[
            'http://owlban-backend-1:5000',
            'http://owlban-backend-2:5000',
            'http://owlban-backend-3:5000'
        ],
        domain='api.owlban.group',
        output_path='/etc/nginx/sites-available/owlban',
        ssl_cert='/etc/ssl/certs/owlban.crt',
        ssl_key='/etc/ssl/private/owlban.key'
    )

if __name__ == "__main__":
    # Generate development configuration
    dev_config = create_development_config()
    print("Development configuration generated")

    # Generate production configuration
    prod_config = create_production_config()
    print("Production configuration generated")
