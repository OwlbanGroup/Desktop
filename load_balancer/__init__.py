"""
Load balancer package
"""

from .nginx_config import generate_nginx_config

__all__ = ['generate_nginx_config']
