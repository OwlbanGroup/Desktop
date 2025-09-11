"""
Enhanced Database connection and session management for Oscar Broome Revenue System
Provides SQLAlchemy engine and session management with MySQL and PostgreSQL support
"""

import os
import logging
import time
from datetime import datetime
from typing import Generator, Optional, Dict, Any
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from urllib.parse import urlparse

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Enhanced database connection manager with connection pooling and health checks"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.metadata = MetaData()
        self._connection_string = self._build_connection_string()

    def _build_connection_string(self) -> str:
        """Build database connection string from environment variables"""
        db_type = os.getenv('DB_TYPE', 'postgresql')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432' if db_type == 'postgresql' else '3306')
        db_name = os.getenv('DB_NAME', 'oscar_broome_revenue')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')

        if db_type.lower() == 'postgresql':
            return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        elif db_type.lower() == 'mysql':
            return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def init_db(self) -> None:
        """Initialize database connection and create tables"""
        try:
            # Create engine with enhanced connection pooling
            self.engine = create_engine(
                self._connection_string,
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

            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Database connection established successfully")

        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def create_tables(self) -> None:
        """Create all database tables"""
        try:
            if self.engine is None:
                raise RuntimeError("Database not initialized. Call init_db() first.")

            # Import models to ensure they are registered with SQLAlchemy
            from .models import Base
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")

        except SQLAlchemyError as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    @contextmanager
    def get_db(self):
        """Get database session with automatic cleanup"""
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")

        db = self.SessionLocal()
        try:
            yield db
        except Exception as e:
            db.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            db.close()

    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive database health check"""
        try:
            start_time = time.time()
            connection_ok = False

            with self.engine.connect() as conn:
                # Test basic connectivity
                result = conn.execute(text("SELECT 1 as health_check, NOW() as current_time"))
                row = result.fetchone()
                connection_ok = True

                # Test connection pool status
                pool_status = {
                    "pool_size": self.engine.pool.size(),
                    "checked_out": self.engine.pool.checkedout(),
                    "overflow": self.engine.pool.overflow(),
                    "invalid": self.engine.pool.invalid()
                }

                # Test database-specific queries
                db_info = {}
                if 'postgresql' in self._connection_string:
                    db_result = conn.execute(text("SELECT version(), current_database()"))
                    db_row = db_result.fetchone()
                    db_info = {
                        "version": str(db_row[0])[:50] + "...",  # Truncate long version string
                        "database_name": str(db_row[1]),
                        "type": "PostgreSQL"
                    }
                elif 'mysql' in self._connection_string:
                    db_result = conn.execute(text("SELECT VERSION(), DATABASE()"))
                    db_row = db_result.fetchone()
                    db_info = {
                        "version": str(db_row[0]),
                        "database_name": str(db_row[1]),
                        "type": "MySQL"
                    }

            response_time = time.time() - start_time

            return {
                "status": "healthy" if connection_ok else "unhealthy",
                "message": "Database connection is working" if connection_ok else "Database connection failed",
                "timestamp": str(row[1]) if connection_ok else str(datetime.utcnow()),
                "pool_status": pool_status,
                "database_info": db_info,
                "response_time_ms": round(response_time * 1000, 2)
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}",
                "timestamp": str(datetime.utcnow()),
                "pool_status": None,
                "database_info": None
            }

    def close(self) -> None:
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")

# Global database manager instance
db_manager = DatabaseManager()

def get_db():
    """Dependency injection for FastAPI/database sessions"""
    return db_manager.get_db()

def init_db():
    """Initialize database connection"""
    db_manager.init_db()

def create_tables():
    """Create database tables"""
    db_manager.create_tables()

def get_db_manager():
    """Get database manager instance"""
    return db_manager

# Initialize database on module import if environment variables are set
if os.getenv('DB_HOST') and os.getenv('DB_NAME'):
    try:
        init_db()
        create_tables()
        logger.info("Database initialized automatically")
    except Exception as e:
        logger.warning(f"Automatic database initialization failed: {e}")
        logger.info("Database will be initialized manually when needed")
