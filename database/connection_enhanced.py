"""
Enhanced Database connection and session management
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Generator, Optional
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration with environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://owlban:password@localhost:5432/owlban_db')
DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
DATABASE_PORT = os.getenv('DATABASE_PORT', '5432')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'owlban_db')
DATABASE_USER = os.getenv('DATABASE_USER', 'owlban')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'password')

# Build DATABASE_URL if not provided
if not DATABASE_URL or DATABASE_URL == 'postgresql://owlban:password@localhost:5432/owlban_db':
    DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Create engine with enhanced connection pooling and error handling
try:
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600,  # Recycle connections after 1 hour
        pool_pre_ping=True,  # Test connections before use
        echo=False,  # Set to True for SQL query logging in development
        connect_args={
            "connect_timeout": 10,
            "application_name": "OSCAR-BROOME-REVENUE"
        }
    )
    logger.info("✅ Database engine created successfully")
except Exception as e:
    logger.error(f"❌ Failed to create database engine: {e}")
    raise

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session
    Use in FastAPI route dependencies or Flask request context
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """
    Context manager for database sessions
    Usage:
        with get_db_context() as db:
            # Use db session
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database transaction failed: {e}")
        raise
    finally:
        db.close()

def init_db():
    """
    Initialize database and create all tables
    Call this once during application startup
    """
    try:
        from .models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        return False

def create_tables():
    """
    Create all database tables
    Alias for init_db for backward compatibility
    """
    return init_db()

def test_connection() -> bool:
    """
    Test database connection
    Returns True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection test successful")
        return True
    except SQLAlchemyError as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during connection test: {e}")
        return False

def get_connection_info() -> dict:
    """
    Get database connection information
    Returns dict with connection details
    """
    try:
        parsed_url = urlparse(DATABASE_URL)
        return {
            'database_url': f"{parsed_url.scheme}://{parsed_url.hostname}:{parsed_url.port}/{parsed_url.path}",
            'pool_size': engine.pool.size(),
            'max_overflow': engine.pool._max_overflow,
            'checked_out': engine.pool.checkedout(),
            'invalid': engine.pool.invalid(),
            'available': engine.pool.size() - engine.pool.checkedout(),
            'engine_status': 'connected' if test_connection() else 'disconnected'
        }
    except Exception as e:
        logger.error(f"❌ Failed to get connection info: {e}")
        return {'error': str(e)}

def health_check() -> dict:
    """
    Comprehensive database health check
    Returns dict with health status and metrics
    """
    try:
        start_time = time.time()
        connection_ok = test_connection()
        response_time = time.time() - start_time

        return {
            'status': 'healthy' if connection_ok else 'unhealthy',
            'response_time_ms': round(response_time * 1000, 2),
            'connection_pool': get_connection_info(),
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

# Import time and datetime for health check
import time
from datetime import datetime
