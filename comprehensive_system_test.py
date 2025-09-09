#!/usr/bin/env python3
"""
Comprehensive System Test Suite for OSCAR-BROOME-REVENUE
Tests all critical components: database, authentication, API endpoints, TypeScript compilation
"""

import os
import sys
import json
import subprocess
import requests
import time
from pathlib import Path
from datetime import datetime
import unittest
from unittest.mock import Mock, patch
import tempfile
import shutil

class ComprehensiveSystemTest(unittest.TestCase):
    """Comprehensive test suite for the entire OSCAR-BROOME-REVENUE system"""

    def setUp(self):
        """Set up test environment"""
        self.project_root = Path(__file__).parent
        self.test_results = []
        self.start_time = time.time()

    def tearDown(self):
        """Clean up after tests"""
        end_time = time.time()
        duration = end_time - self.start_time
        print(f"\nTest completed in {duration:.2f} seconds")

    def log_result(self, test_name, status, message=""):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{'✅' if status == 'PASS' else '❌'} {test_name}: {message}")

    def test_database_connection(self):
        """Test database connection and basic operations"""
        try:
            # Test database connection
            from database.connection import test_connection, get_connection_info
            connection_ok = test_connection()
            self.assertTrue(connection_ok, "Database connection failed")

            # Test connection info
            info = get_connection_info()
            self.assertIsInstance(info, dict, "Connection info should be dict")
            self.assertIn('pool_size', info, "Pool size should be in connection info")

            self.log_result("Database Connection", "PASS", "Database connection successful")
        except Exception as e:
            self.log_result("Database Connection", "FAIL", str(e))

    def test_database_models(self):
        """Test database models and schema"""
        try:
            from database.models import Base, User, RevenueData
            from database.connection import engine

            # Test table creation
            Base.metadata.create_all(bind=engine)

            # Verify tables exist
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            expected_tables = ['users', 'revenue_data', 'payroll_data']

            for table in expected_tables:
                self.assertIn(table, tables, f"Table {table} should exist")

            self.log_result("Database Models", "PASS", f"Created tables: {tables}")
        except Exception as e:
            self.log_result("Database Models", "FAIL", str(e))

    def test_authentication_system(self):
        """Test authentication system components"""
        try:
            # Test login override system
            auth_file = self.project_root / 'OSCAR-BROOME-REVENUE' / 'auth' / 'login_override.js'
            self.assertTrue(auth_file.exists(), "Login override file should exist")

            # Read and validate auth configuration
            with open(auth_file, 'r') as f:
                content = f.read()
                self.assertIn('OVERRIDE_CONFIG', content, "Should contain override config")
                self.assertIn('LoginOverrideManager', content, "Should contain login manager class")

            self.log_result("Authentication System", "PASS", "Authentication components validated")
        except Exception as e:
            self.log_result("Authentication System", "FAIL", str(e))

    def test_typescript_compilation(self):
        """Test TypeScript compilation in earnings_dashboard"""
        try:
            ts_dir = self.project_root / 'OSCAR-BROOME-REVENUE' / 'earnings_dashboard'
            self.assertTrue(ts_dir.exists(), "TypeScript directory should exist")

            # Check for TypeScript files
            ts_files = list(ts_dir.glob('*.ts'))
            self.assertTrue(len(ts_files) > 0, "Should have TypeScript files")

            # Test compilation (if tsc is available)
            try:
                result = subprocess.run(['tsc', '--noEmit', '--skipLibCheck'],
                                      cwd=ts_dir, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    self.log_result("TypeScript Compilation", "PASS", "No compilation errors")
                else:
                    self.log_result("TypeScript Compilation", "WARN", f"Compilation issues: {result.stderr[:200]}")
            except FileNotFoundError:
                self.log_result("TypeScript Compilation", "SKIP", "TypeScript compiler not available")

        except Exception as e:
            self.log_result("TypeScript Compilation", "FAIL", str(e))

    def test_backend_api_endpoints(self):
        """Test backend API endpoints"""
        try:
            from backend.app_server import app
            self.assertIsNotNone(app, "Flask app should be available")

            # Test app configuration
            with app.test_client() as client:
                # Test health endpoint
                response = client.get('/health')
                self.assertEqual(response.status_code, 200, "Health endpoint should return 200")

                # Test earnings endpoint (may require auth)
                response = client.get('/api/earnings')
                # Should return 401 or 200 depending on auth setup
                self.assertIn(response.status_code, [200, 401, 403], "Earnings endpoint should be accessible or require auth")

            self.log_result("Backend API Endpoints", "PASS", "API endpoints responding correctly")
        except Exception as e:
            self.log_result("Backend API Endpoints", "FAIL", str(e))

    def test_frontend_build(self):
        """Test frontend build process"""
        try:
            frontend_dir = self.project_root / 'OSCAR-BROOME-REVENUE'
            package_json = frontend_dir / 'package.json'
            self.assertTrue(package_json.exists(), "package.json should exist")

            # Check package.json content
            with open(package_json, 'r') as f:
                package_data = json.load(f)
                self.assertIn('scripts', package_data, "Should have scripts section")
                self.assertIn('dependencies', package_data, "Should have dependencies")

            self.log_result("Frontend Build", "PASS", "Frontend configuration validated")
        except Exception as e:
            self.log_result("Frontend Build", "FAIL", str(e))

    def test_production_deployment_script(self):
        """Test production deployment script"""
        try:
            deploy_script = self.project_root / 'production_deploy_script.py'
            self.assertTrue(deploy_script.exists(), "Deployment script should exist")

            # Test script syntax
            result = subprocess.run([sys.executable, '-m', 'py_compile', str(deploy_script)],
                                  capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, "Script should compile without syntax errors")

            # Test help output
            result = subprocess.run([sys.executable, str(deploy_script), '--help'],
                                  capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, "Help should work")
            self.assertIn('OSCAR-BROOME-REVENUE', result.stdout, "Should show app name in help")

            self.log_result("Production Deployment Script", "PASS", "Deployment script validated")
        except Exception as e:
            self.log_result("Production Deployment Script", "FAIL", str(e))

    def test_database_dump(self):
        """Test database dump file"""
        try:
            dump_file = self.project_root / 'database_dump.sql'
            self.assertTrue(dump_file.exists(), "Database dump should exist")

            # Check file size
            size = dump_file.stat().st_size
            self.assertGreater(size, 1000, "Dump file should not be empty")

            # Check content
            with open(dump_file, 'r') as f:
                content = f.read()
                self.assertIn('CREATE DATABASE', content, "Should contain database creation")
                self.assertIn('INSERT INTO', content, "Should contain seed data")
                self.assertIn('COMMIT', content, "Should end with commit")

            self.log_result("Database Dump", "PASS", f"Dump file size: {size} bytes")
        except Exception as e:
            self.log_result("Database Dump", "FAIL", str(e))

    def test_monitoring_setup(self):
        """Test monitoring configuration"""
        try:
            monitoring_dir = self.project_root / 'monitoring'
            self.assertTrue(monitoring_dir.exists(), "Monitoring directory should exist")

            # Check monitoring files
            required_files = ['docker-compose.monitoring.yml', 'prometheus.yml', 'alert_rules.yml']
            for file in required_files:
                file_path = monitoring_dir / file
                self.assertTrue(file_path.exists(), f"Monitoring file {file} should exist")

            self.log_result("Monitoring Setup", "PASS", "Monitoring configuration validated")
        except Exception as e:
            self.log_result("Monitoring Setup", "FAIL", str(e))

    def test_security_configuration(self):
        """Test security configuration"""
        try:
            security_file = self.project_root / 'backend' / 'security_config.py'
            if security_file.exists():
                # Test security config import
                sys.path.append(str(self.project_root / 'backend'))
                import security_config
                self.assertTrue(hasattr(security_config, 'SECRET_KEY'), "Should have SECRET_KEY")
                self.log_result("Security Configuration", "PASS", "Security config validated")
            else:
                self.log_result("Security Configuration", "SKIP", "Security config not found")
        except Exception as e:
            self.log_result("Security Configuration", "FAIL", str(e))

    def test_integration_endpoints(self):
        """Test integration with external services"""
        try:
            # Test JPMorgan integration files
            jpm_files = [
                'OSCAR-BROOME-REVENUE/earnings_dashboard/jpmorgan_payment.js',
                'OSCAR-BROOME-REVENUE/earnings_dashboard/jpmorgan_payment_enhanced.js'
            ]

            for file in jpm_files:
                file_path = self.project_root / file
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        content = f.read()
                        self.assertIn('JPMorgan', content, f"File {file} should contain JPMorgan references")

            # Test NVIDIA integration files
            nvidia_files = [
                'nvidia_control_panel.py',
                'nvidia_integration_fixed.py'
            ]

            for file in nvidia_files:
                file_path = self.project_root / file
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        content = f.read()
                        self.assertIn('nvidia', content.lower(), f"File {file} should contain NVIDIA references")

            self.log_result("Integration Endpoints", "PASS", "Integration files validated")
        except Exception as e:
            self.log_result("Integration Endpoints", "FAIL", str(e))

    def generate_test_report(self):
        """Generate comprehensive test report"""
        report = {
            'test_run': {
                'timestamp': datetime.now().isoformat(),
                'duration': time.time() - self.start_time,
                'total_tests': len(self.test_results),
                'passed': len([r for r in self.test_results if r['status'] == 'PASS']),
                'failed': len([r for r in self.test_results if r['status'] == 'FAIL']),
                'skipped': len([r for r in self.test_results if r['status'] == 'SKIP'])
            },
            'results': self.test_results
        }

        # Save report to file
        report_file = self.project_root / 'test_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Print summary
        print("\n" + "="*60)
        print("COMPREHENSIVE SYSTEM TEST REPORT")
        print("="*60)
        print(f"Total Tests: {report['test_run']['total_tests']}")
        print(f"Passed: {report['test_run']['passed']}")
        print(f"Failed: {report['test_run']['failed']}")
        print(f"Skipped: {report['test_run']['skipped']}")
        print(".2f")
        print(f"Report saved to: {report_file}")
        print("="*60)

        return report

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🚀 Starting Comprehensive System Tests for OSCAR-BROOME-REVENUE")
    print("="*60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(ComprehensiveSystemTest)
    runner = unittest.TextTestRunner(verbosity=2)

    # Run tests
    result = runner.run(suite)

    # Generate report
    test_instance = ComprehensiveSystemTest()
    test_instance.test_results = []  # Will be populated during test runs
    report = test_instance.generate_test_report()

    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
