"""
Configuration file for Owlban Group Integrated Platform
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Server configuration
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"

# NVIDIA Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_NIM_SERVICE_URL = os.getenv("NVIDIA_NIM_SERVICE_URL")
CUDA_VISIBLE_DEVICES = os.getenv("CUDA_VISIBLE_DEVICES", "0")

# Database configuration (for future use)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///owlban_group.db")

# Revenue tracking configuration
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "USD")
REVENUE_TRACKING_ENABLED = os.getenv("REVENUE_TRACKING_ENABLED", "true").lower() == "true"

# Leadership simulation configuration
DEFAULT_LEADER_NAME = os.getenv("DEFAULT_LEADER_NAME", "Alice")
DEFAULT_LEADERSHIP_STYLE = os.getenv("DEFAULT_LEADERSHIP_STYLE", "DEMOCRATIC")
DEFAULT_TEAM_MEMBERS = os.getenv("DEFAULT_TEAM_MEMBERS", "Bob:Developer,Charlie:Designer").split(",")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "owlban_group.log")

# Security configuration (for future use)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour

# API configuration
API_PREFIX = "/api"
API_VERSION = "v1"

# Frontend configuration
STATIC_FOLDER = FRONTEND_DIR
TEMPLATE_FOLDER = FRONTEND_DIR

# Test configuration
TESTING = os.getenv("TESTING", "false").lower() == "true"
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///test_owlban_group.db")

def get_config():
    """Return configuration as dictionary"""
    return {
        "server": {
            "host": SERVER_HOST,
            "port": SERVER_PORT,
            "debug": DEBUG_MODE
        },
        "nvidia": {
            "api_key": NVIDIA_API_KEY,
            "nim_service_url": NVIDIA_NIM_SERVICE_URL,
            "cuda_visible_devices": CUDA_VISIBLE_DEVICES
        },
        "database": {
            "url": DATABASE_URL
        },
        "leadership": {
            "default_leader": DEFAULT_LEADER_NAME,
            "default_style": DEFAULT_LEADERSHIP_STYLE,
            "default_team": DEFAULT_TEAM_MEMBERS
        },
        "logging": {
            "level": LOG_LEVEL,
            "file": LOG_FILE
        }
    }

def validate_config():
    """Validate configuration and return any issues"""
    issues = []

    # Check required directories
    if not BACKEND_DIR.exists():
        issues.append(f"Backend directory not found: {BACKEND_DIR}")

    if not FRONTEND_DIR.exists():
        issues.append(f"Frontend directory not found: {FRONTEND_DIR}")

    # Check NVIDIA configuration
    if not NVIDIA_API_KEY:
        issues.append("NVIDIA_API_KEY environment variable not set (optional for basic functionality)")

    return issues
