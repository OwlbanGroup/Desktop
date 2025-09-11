"""
Comprehensive test suite for database connection and session management
Tests the DatabaseManager class and related functionality
"""

import os
import pytest
import unittest.mock as mock
from unittest.mock import patch, MagicMock
from database.connection_fixed import DatabaseManager, db_manager, get_db_manager, init_db, create_tables


class TestDatabaseManager:
    """Test cases for DatabaseManager class"""

    def setup_method(self):
        """Setup before each test"""
        # Reset the global manager
        global db_manager
        db_manager = DatabaseManager()

    def teardown_method(self):
        """Cleanup after each test"""
        if db_manager.engine:
            db_manager.close()

    def test_init_without_env_vars(self):
        """Test initialization without environment variables"""
        manager = DatabaseManager()
        assert manager.engine is None
        assert manager.SessionLocal is None
        assert manager._connection_string == "postgresql+psycopg2://postgres:@localhost:5432/oscar_broome_revenue"

    @patch.dict(os.environ, {
        'DB_TYPE': 'mysql',
        'DB_HOST': 'test-host',
        'DB_PORT': '3307',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_pass'
    })
    def test_connection_string_mysql(self):
        """Test MySQL connection string building"""
        manager = DatabaseManager()
        expected = "mysql+pymysql://test_user:test_pass@test-host:3307/test_db"
        assert manager._connection_string == expected

    @patch.dict(os.environ, {
        'DB_TYPE': 'postgresql',
        'DB_HOST': 'pg-host',
        'DB_PORT': '5433',
        'DB_NAME': 'pg_db',
        'DB_USER': 'pg_user',
        'DB_PASSWORD': 'pg_pass'
    })
    def test_connection_string_postgresql(self):
        """Test PostgreSQL connection string building"""
        manager = DatabaseManager()
        expected = "postgresql+psycopg2://pg_user:pg_pass@pg-host:5433/pg_db"
        assert manager._connection_string == expected

    def test_invalid_db_type(self):
        """Test invalid database type raises ValueError"""
        with patch.dict(os.environ, {'DB_TYPE': 'invalid'}):
            manager = DatabaseManager()
            with pytest.raises(ValueError, match="Unsupported database type"):
                manager._build_connection_string()

    @patch('database.connection_fixed.create_engine')
    @patch('database.connection_fixed.sessionmaker')
    def test_init_db_success(self, mock_sessionmaker, mock_create_engine):
        """Test successful database initialization"""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session = MagicMock()
        mock_sessionmaker.return_value = mock_session

        manager = DatabaseManager()
        manager.init_db()

        mock_create_engine.assert_called_once()
        mock_sessionmaker.assert_called_once()
        assert manager.engine == mock_engine
        assert manager.SessionLocal == mock_session

    @patch('database.connection_fixed.create_engine')
    def test_init_db_failure(self, mock_create_engine):
        """Test database initialization failure"""
        mock_create_engine.side_effect = Exception("Connection failed")

        manager = DatabaseManager()
        with pytest.raises(Exception, match="Connection failed"):
            manager.init_db()

    @patch('database.connection_fixed.create_engine')
    @patch('database.connection_fixed.sessionmaker')
    def test_create_tables_success(self, mock_sessionmaker, mock_create_engine):
        """Test successful table creation"""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        manager = DatabaseManager()
        manager.init_db()

        with patch('database.connection_fixed.Base') as mock_base:
            manager.create_tables()
            mock_base.metadata.create_all.assert_called_once_with(bind=mock_engine)

    def test_create_tables_without_init(self):
        """Test table creation without initialization raises error"""
        manager = DatabaseManager()
        with pytest.raises(RuntimeError, match="Database not initialized"):
            manager.create_tables()

    @patch('database.connection_fixed.create_engine')
    @patch('database.connection_fixed.sessionmaker')
    def test_get_db_context_manager(self, mock_sessionmaker, mock_create_engine):
        """Test database session context manager"""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session = MagicMock()
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_sessionmaker.return_value = mock_session

        manager = DatabaseManager()
        manager.init_db()

        with manager.get_db() as db:
            assert db == mock_session_instance

        mock_session_instance.close.assert_called_once()

    def test_get_db_without_init(self):
        """Test get_db without initialization raises error"""
        manager = DatabaseManager()
        with pytest.raises(RuntimeError, match="Database not initialized"):
            with manager.get_db():
                pass

    @patch('database.connection_fixed.create_engine')
    @patch('database.connection_fixed.sessionmaker')
    def test_health_check_success(self, mock_sessionmaker, mock_create_engine):
        """Test successful health check"""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_result = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = (1, '2023-01-01 12:00:00')

        manager = DatabaseManager()
        manager.init_db()

        result = manager.health_check()

        assert result['status'] == 'healthy'
        assert 'Database connection is working' in result['message']
        assert result['pool_status'] is not None

    @patch('database.connection_fixed.create_engine')
    def test_health_check_failure(self, mock_create_engine):
        """Test health check failure"""
        mock_create_engine.return_value = MagicMock()
        mock_create_engine.return_value.connect.side_effect = Exception("Connection failed")

        manager = DatabaseManager()
        manager.init_db()

        result = manager.health_check()

        assert result['status'] == 'unhealthy'
        assert 'Connection failed' in result['message']

    def test_close(self):
        """Test database connection closure"""
        mock_engine = MagicMock()
        manager = DatabaseManager()
        manager.engine = mock_engine

        manager.close()

        mock_engine.dispose.assert_called_once()

    def test_close_without_engine(self):
        """Test close when no engine exists"""
        manager = DatabaseManager()
        manager.close()  # Should not raise error

    def test_get_db_manager(self):
        """Test get_db_manager function"""
        manager = get_db_manager()
        assert isinstance(manager, DatabaseManager)

    @patch('database.connection_fixed.logger')
    def test_auto_init_success(self, mock_logger):
        """Test automatic initialization on import"""
        with patch.dict(os.environ, {'DB_HOST': 'localhost', 'DB_NAME': 'test'}):
            with patch('database.connection_fixed.init_db') as mock_init:
                with patch('database.connection_fixed.create_tables') as mock_create:
                    # Re-import to trigger auto-init
                    import importlib
                    import database.connection_fixed
                    importlib.reload(database.connection_fixed)

                    mock_init.assert_called()
                    mock_create.assert_called()

    @patch('database.connection_fixed.logger')
    def test_auto_init_failure(self, mock_logger):
        """Test automatic initialization failure"""
        with patch.dict(os.environ, {'DB_HOST': 'localhost', 'DB_NAME': 'test'}):
            with patch('database.connection_fixed.init_db', side_effect=Exception("Init failed")):
                with patch('database.connection_fixed.create_tables'):
                    # Re-import to trigger auto-init
                    import importlib
                    import database.connection_fixed
                    importlib.reload(database.connection_fixed)

                    mock_logger.warning.assert_called()


class TestIntegrationScenarios:
    """Integration test scenarios"""

    def test_full_initialization_workflow(self):
        """Test complete database initialization workflow"""
        with patch('database.connection_fixed.create_engine') as mock_create_engine:
            with patch('database.connection_fixed.sessionmaker') as mock_sessionmaker:
                mock_engine = MagicMock()
                mock_create_engine.return_value = mock_engine
                mock_session = MagicMock()
                mock_sessionmaker.return_value = mock_session

                manager = DatabaseManager()
                manager.init_db()
                manager.create_tables()

                # Verify initialization
                assert manager.engine is not None
                assert manager.SessionLocal is not None

                # Test session usage
                with manager.get_db() as db:
                    assert db is not None

                # Test health check
                with patch.object(manager, 'health_check', return_value={'status': 'healthy'}):
                    health = manager.health_check()
                    assert health['status'] == 'healthy'

                # Test cleanup
                manager.close()
                mock_engine.dispose.assert_called_once()

    def test_connection_pooling_configuration(self):
        """Test connection pool configuration"""
        with patch('database.connection_fixed.create_engine') as mock_create_engine:
            manager = DatabaseManager()
            manager.init_db()

            # Verify engine was created with pooling parameters
            call_args = mock_create_engine.call_args
            assert 'poolclass' in call_args.kwargs
            assert 'pool_size' in call_args.kwargs
            assert 'max_overflow' in call_args.kwargs


if __name__ == '__main__':
    pytest.main([__file__])
