"""
Database connection and session management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://owlban:password@localhost:5432/owlban_db')

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False  # Set to True for SQL query logging in development
)

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
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """
    Initialize database and create all tables
    Call this once during application startup
    """
    from .models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def create_tables():
    """
    Create all database tables
    Alias for init_db for backward compatibility
    """
    init_db()

def test_connection():
    """
    Test database connection
    Returns True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def get_connection_info():
    """
    Get database connection information
    Returns dict with connection details
    """
    return {
        'database_url': DATABASE_URL.replace(DATABASE_URL.split('@')[0].split(':')[-1], '***'),  # Hide password
        'pool_size': engine.pool.size(),
        'max_overflow': engine.pool._max_overflow,
        'checked_out': engine.pool.checkedout(),
        'invalid': engine.pool.invalid(),
        'available': engine.pool.size() - engine.pool.checkedout()
    }
