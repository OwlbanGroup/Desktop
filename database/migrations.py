#!/usr/bin/env python3
"""
Database Migration and Setup Script
Handles database initialization, migrations, and schema management
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config
from alembic.environment import EnvironmentContext
from alembic.script import ScriptDirectory

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from database.models import Base
from database.connection import engine, test_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database operations and migrations"""

    def __init__(self, database_url=None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'postgresql://owlban:password@localhost:5432/owlban_db')
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False

    def create_database(self):
        """Create database if it doesn't exist"""
        try:
            # Connect to default database to create the target database
            default_url = self.database_url.replace('/owlban_db', '/postgres')
            temp_engine = create_engine(default_url)

            with temp_engine.connect() as conn:
                conn.execute(text("COMMIT"))  # Close any open transactions
                conn.execute(text("CREATE DATABASE owlban_db"))
                logger.info("✅ Database 'owlban_db' created successfully")

        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info("ℹ️  Database 'owlban_db' already exists")
            else:
                logger.error(f"❌ Failed to create database: {e}")
                raise

    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ All database tables created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            raise

    def drop_tables(self):
        """Drop all database tables (dangerous operation)"""
        try:
            confirm = input("⚠️  This will drop all tables. Are you sure? (type 'YES' to confirm): ")
            if confirm != 'YES':
                logger.info("Operation cancelled")
                return

            Base.metadata.drop_all(bind=self.engine)
            logger.info("✅ All database tables dropped successfully")
        except Exception as e:
            logger.error(f"❌ Failed to drop tables: {e}")
            raise

    def seed_database(self):
        """Seed database with initial data"""
        try:
            from database.models import User, LeadershipSession, RevenueRecord

            with self.SessionLocal() as session:
                # Create admin user
                admin_user = User(
                    username='admin',
                    email='admin@owlban.com',
                    password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCt1uB0Y1uEXeGcK',  # password: admin123
                    role='admin',
                    is_active=True
                )

                # Check if admin user already exists
                existing_admin = session.query(User).filter_by(username='admin').first()
                if not existing_admin:
                    session.add(admin_user)
                    logger.info("✅ Admin user created")
                else:
                    logger.info("ℹ️  Admin user already exists")

                # Create sample revenue records
                sample_revenue = [
                    RevenueRecord(
                        source='NVIDIA GPU Sales',
                        amount=150000.00,
                        category='Hardware Sales',
                        description='Q4 GPU sales revenue'
                    ),
                    RevenueRecord(
                        source='Leadership Consulting',
                        amount=75000.00,
                        category='Services',
                        description='Executive leadership training'
                    )
                ]

                for revenue in sample_revenue:
                    session.add(revenue)

                session.commit()
                logger.info("✅ Sample data seeded successfully")

        except Exception as e:
            logger.error(f"❌ Failed to seed database: {e}")
            raise

    def backup_database(self, backup_path=None):
        """Create database backup"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_path or f"backup_{timestamp}.sql"

            # Use pg_dump for PostgreSQL
            if 'postgresql' in self.database_url:
                os.system(f"pg_dump '{self.database_url}' > {backup_file}")
            else:
                logger.error("❌ Backup not supported for this database type")
                return

            logger.info(f"✅ Database backup created: {backup_file}")
            return backup_file

        except Exception as e:
            logger.error(f"❌ Failed to create backup: {e}")
            raise

    def restore_database(self, backup_file):
        """Restore database from backup"""
        try:
            if not os.path.exists(backup_file):
                raise FileNotFoundError(f"Backup file not found: {backup_file}")

            # Use psql for PostgreSQL
            if 'postgresql' in self.database_url:
                os.system(f"psql '{self.database_url}' < {backup_file}")
            else:
                logger.error("❌ Restore not supported for this database type")
                return

            logger.info(f"✅ Database restored from: {backup_file}")

        except Exception as e:
            logger.error(f"❌ Failed to restore database: {e}")
            raise

    def run_migrations(self):
        """Run database migrations using Alembic"""
        try:
            # Initialize Alembic if not already done
            if not os.path.exists('alembic'):
                os.makedirs('alembic')

            # Create alembic.ini if it doesn't exist
            alembic_cfg = Config('alembic.ini')
            alembic_cfg.set_main_option('script_location', 'database:migrations')
            alembic_cfg.set_main_option('sqlalchemy.url', self.database_url)

            # Run migrations
            command.upgrade(alembic_cfg, 'head')
            logger.info("✅ Database migrations completed successfully")

        except Exception as e:
            logger.error(f"❌ Failed to run migrations: {e}")
            raise

    def get_database_info(self):
        """Get database information and statistics"""
        try:
            info = {
                'database_url': self.database_url.replace(self.database_url.split('@')[0].split(':')[-1], '***'),
                'tables': [],
                'connection_count': 0
            }

            with self.engine.connect() as conn:
                # Get table names
                if 'postgresql' in self.database_url:
                    result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
                    info['tables'] = [row[0] for row in result]

                    # Get connection count
                    result = conn.execute(text("SELECT count(*) FROM pg_stat_activity"))
                    info['connection_count'] = result.fetchone()[0]

            return info

        except Exception as e:
            logger.error(f"❌ Failed to get database info: {e}")
            return None

def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(description='Database Management Tool')
    parser.add_argument('action', choices=[
        'test', 'create', 'init', 'drop', 'seed', 'backup', 'restore',
        'migrate', 'info', 'setup'
    ], help='Database action to perform')
    parser.add_argument('--backup-file', help='Backup file path for restore')
    parser.add_argument('--database-url', help='Database URL override')

    args = parser.parse_args()

    # Initialize database manager
    db_manager = DatabaseManager(args.database_url)

    try:
        if args.action == 'test':
            success = db_manager.test_connection()
            sys.exit(0 if success else 1)

        elif args.action == 'create':
            db_manager.create_database()

        elif args.action == 'init':
            db_manager.create_database()
            db_manager.create_tables()

        elif args.action == 'drop':
            db_manager.drop_tables()

        elif args.action == 'seed':
            db_manager.seed_database()

        elif args.action == 'backup':
            backup_file = db_manager.backup_database()
            print(f"Backup created: {backup_file}")

        elif args.action == 'restore':
            if not args.backup_file:
                print("❌ --backup-file required for restore action")
                sys.exit(1)
            db_manager.restore_database(args.backup_file)

        elif args.action == 'migrate':
            db_manager.run_migrations()

        elif args.action == 'info':
            info = db_manager.get_database_info()
            if info:
                print("Database Information:")
                print(f"  URL: {info['database_url']}")
                print(f"  Tables: {', '.join(info['tables'])}")
                print(f"  Active Connections: {info['connection_count']}")

        elif args.action == 'setup':
            print("🚀 Setting up complete database environment...")
            db_manager.create_database()
            db_manager.create_tables()
            db_manager.seed_database()
            print("✅ Database setup completed successfully!")

    except Exception as e:
        logger.error(f"❌ Operation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
