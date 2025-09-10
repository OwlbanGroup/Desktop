"""
Database connection and session management for Oscar Broome Revenue System
Provides SQLAlchemy engine and session management with MySQL and PostgreSQL support
"""

import os
import logging
from typing import Optional, Any
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection manager with connection pooling and health checks"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.metadata = MetaData()
        self._connection_string = self._build_connection_string()

    def _build_connection_string(self) -> str:
        """Build database connection string from environment variables"""
        db_type = os.getenv('DB_TYPE', 'mysql')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '3306' if db_type == 'mysql' else '5432')
        db_name = os.getenv('DB_NAME', 'oscar_broome_revenue')
        db_user = os.getenv('DB_USER', 'root')
        db_password = os.getenv('DB_PASSWORD', '')

        if db_type.lower() == 'mysql':
            return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        elif db_type.lower() == 'postgresql':
            return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def init_db(self) -> None:
        """Initialize database connection and create tables"""
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                self._connection_string,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=3600,  # Recycle connections after 1 hour
                echo=False  # Set to True for SQL query logging in development
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

    def health_check(self) -> dict:
        """Perform comprehensive database health check"""
        try:
            with self.engine.connect() as conn:
                # Test basic connectivity
                result = conn.execute(text("SELECT 1 as health_check, NOW() as current_time"))
                row = result.fetchone()

                # Test connection pool status
                pool_status = {
                    "pool_size": self.engine.pool.size(),
                    "checked_out": self.engine.pool.checkedout(),
                    "overflow": self.engine.pool.overflow(),
                    "invalid": self.engine.pool.invalid()
                }

                # Test database-specific queries
                db_info = {}
                if self._connection_string.startswith('mysql'):
                    db_result = conn.execute(text("SELECT VERSION() as version, DATABASE() as database_name"))
                    db_row = db_result.fetchone()
                    db_info = {
                        "version": db_row[0],
                        "database_name": db_row[1],
                        "type": "MySQL"
                    }
                elif self._connection_string.startswith('postgresql'):
                    db_result = conn.execute(text("SELECT version(), current_database()"))
                    db_row = db_result.fetchone()
                    db_info = {
                        "version": db_row[0][:50] + "...",  # Truncate long version string
                        "database_name": db_row[1],
                        "type": "PostgreSQL"
                    }

                return {
                    "status": "healthy",
                    "message": "Database connection is working",
                    "timestamp": str(row[1]),
                    "pool_status": pool_status,
                    "database_info": db_info,
                    "response_time_ms": 0  # Could be enhanced with timing
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}",
                "timestamp": str(e),
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
