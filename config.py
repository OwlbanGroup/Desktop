"""
Configuration settings for Owlban Group Integrated Platform
"""

import os

class Config:
    # Database URL for SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://owlban:password@localhost:5432/owlban_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key for session management and JWT
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')

    # JWT configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwtsecretkey')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # seconds

    # Redis cache configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # NVIDIA API key
    NVIDIA_API_KEY = os.getenv('NVIDIA_API_KEY', '')

    # OSCAR BROOME URL for payment and overrides proxy
    OSCAR_BROOME_URL = os.getenv('OSCAR_BROOME_URL', 'http://localhost:4000')

    # Flask environment
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # Debug mode
    DEBUG = FLASK_ENV == 'development'

    # SSL/TLS settings
    SSL_CERT_PATH = os.getenv('SSL_CERT_PATH', '')
    SSL_KEY_PATH = os.getenv('SSL_KEY_PATH', '')

    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Other configurations can be added here as needed
