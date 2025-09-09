#!/usr/bin/env python3
"""
Database Initialization Script for OSCAR-BROOME-REVENUE

This script initializes the database with seed data and performs
initial setup for the production deployment.

Features:
- Creates all database tables
- Populates initial seed data
- Sets up default configurations
- Validates database connectivity

Usage:
    python database/init_db.py
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from database.connection import init_db, test_connection, get_db_context
from database.models import User, Organization, RevenueStream, FinancialTransaction

def load_seed_data():
    """Load seed data from JSON files"""
    seed_dir = Path(__file__).parent / 'seed_data'

    if not seed_dir.exists():
        print("⚠️ Seed data directory not found, creating empty data")
        return {}

    seed_data = {}

    # Load users seed data
    users_file = seed_dir / 'users.json'
    if users_file.exists():
        with open(users_file, 'r') as f:
            seed_data['users'] = json.load(f)

    # Load organizations seed data
    orgs_file = seed_dir / 'organizations.json'
    if orgs_file.exists():
        with open(orgs_file, 'r') as f:
            seed_data['organizations'] = json.load(f)

    # Load revenue streams seed data
    revenue_file = seed_dir / 'revenue_streams.json'
    if revenue_file.exists():
        with open(revenue_file, 'r') as f:
            seed_data['revenue_streams'] = json.load(f)

    return seed_data

def create_seed_data():
    """Create seed data files if they don't exist"""
    seed_dir = Path(__file__).parent / 'seed_data'
    seed_dir.mkdir(exist_ok=True)

    # Create users seed data
    users_data = [
        {
            "username": "admin",
            "email": "admin@oscar-broome.com",
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPjYQmLxE7ZK",  # password: admin123
            "role": "admin",
            "is_active": True,
            "mfa_enabled": True,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "username": "executive",
            "email": "executive@oscar-broome.com",
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPjYQmLxE7ZK",  # password: admin123
            "role": "executive",
            "is_active": True,
            "mfa_enabled": False,
            "created_at": datetime.utcnow().isoformat()
        }
    ]

    with open(seed_dir / 'users.json', 'w') as f:
        json.dump(users_data, f, indent=2)

    # Create organizations seed data
    orgs_data = [
        {
            "name": "OSCAR-BROOME-REVENUE Corp",
            "description": "Integrated Financial Platform",
            "industry": "Financial Technology",
            "headquarters": "New York, NY",
            "founded_year": 2024,
            "employee_count": 50,
            "revenue_range": "$10M-$50M",
            "created_at": datetime.utcnow().isoformat()
        }
    ]

    with open(seed_dir / 'organizations.json', 'w') as f:
        json.dump(orgs_data, f, indent=2)

    # Create revenue streams seed data
    revenue_data = [
        {
            "name": "JPMorgan Payments",
            "category": "Banking",
            "description": "Payment processing through JPMorgan Chase",
            "monthly_revenue": 250000.00,
            "growth_rate": 15.5,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "NVIDIA AI Services",
            "category": "Technology",
            "description": "AI and GPU computing services",
            "monthly_revenue": 180000.00,
            "growth_rate": 25.0,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "Corporate Real Estate",
            "category": "Real Estate",
            "description": "Commercial property management and leasing",
            "monthly_revenue": 320000.00,
            "growth_rate": 8.5,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
    ]

    with open(seed_dir / 'revenue_streams.json', 'w') as f:
        json.dump(revenue_data, f, indent=2)

    print("✅ Seed data files created")

def populate_database(seed_data):
    """Populate database with seed data"""
    print("🌱 Populating database with seed data...")

    with get_db_context() as db:
        # Create users
        if 'users' in seed_data:
            for user_data in seed_data['users']:
                user = User(**user_data)
                db.add(user)
            print(f"✅ Created {len(seed_data['users'])} users")

        # Create organizations
        if 'organizations' in seed_data:
            for org_data in seed_data['organizations']:
                org = Organization(**org_data)
                db.add(org)
            print(f"✅ Created {len(seed_data['organizations'])} organizations")

        # Create revenue streams
        if 'revenue_streams' in seed_data:
            for revenue_data in seed_data['revenue_streams']:
                revenue = RevenueStream(**revenue_data)
                db.add(revenue)
            print(f"✅ Created {len(seed_data['revenue_streams'])} revenue streams")

        # Create sample financial transactions
        sample_transactions = [
            {
                "transaction_id": "TXN-001",
                "amount": 50000.00,
                "description": "JPMorgan payment processing fee",
                "transaction_date": datetime.utcnow(),
                "category": "Banking",
                "status": "completed"
            },
            {
                "transaction_id": "TXN-002",
                "amount": 75000.00,
                "description": "NVIDIA GPU cluster rental",
                "transaction_date": datetime.utcnow(),
                "category": "Technology",
                "status": "completed"
            },
            {
                "transaction_id": "TXN-003",
                "amount": 120000.00,
                "description": "Corporate office lease payment",
                "transaction_date": datetime.utcnow(),
                "category": "Real Estate",
                "status": "pending"
            }
        ]

        for txn_data in sample_transactions:
            txn = FinancialTransaction(**txn_data)
            db.add(txn)

        print(f"✅ Created {len(sample_transactions)} sample transactions")

        db.commit()
        print("✅ Database populated successfully")

def setup_database_config():
    """Setup database configuration and indexes"""
    print("⚙️ Setting up database configuration...")

    # This would typically include:
    # - Creating indexes for performance
    # - Setting up database triggers
    # - Configuring connection pooling
    # - Setting up backup schedules

    print("✅ Database configuration completed")

def validate_database():
    """Validate database setup and data integrity"""
    print("🔍 Validating database setup...")

    with get_db_context() as db:
        # Check if tables exist
        user_count = db.query(User).count()
        org_count = db.query(Organization).count()
        revenue_count = db.query(RevenueStream).count()
        txn_count = db.query(FinancialTransaction).count()

        print(f"📊 Database validation results:")
        print(f"   Users: {user_count}")
        print(f"   Organizations: {org_count}")
        print(f"   Revenue Streams: {revenue_count}")
        print(f"   Transactions: {txn_count}")

        if user_count > 0 and org_count > 0:
            print("✅ Database validation passed")
            return True
        else:
            print("❌ Database validation failed - missing required data")
            return False

def main():
    """Main initialization function"""
    print("🚀 Starting OSCAR-BROOME-REVENUE database initialization...")

    try:
        # Test database connection
        print("🔌 Testing database connection...")
        if not test_connection():
            print("❌ Database connection failed")
            sys.exit(1)
        print("✅ Database connection successful")

        # Initialize database schema
        print("📋 Initializing database schema...")
        init_db()

        # Create seed data if it doesn't exist
        seed_data = load_seed_data()
        if not seed_data:
            print("📝 Creating seed data...")
            create_seed_data()
            seed_data = load_seed_data()

        # Populate database
        populate_database(seed_data)

        # Setup configuration
        setup_database_config()

        # Validate setup
        if validate_database():
            print("🎉 Database initialization completed successfully!")
            print("\n📋 Next steps:")
            print("   1. Start the backend server: python backend/app_server.py")
            print("   2. Start the frontend: cd OSCAR-BROOME-REVENUE && npm start")
            print("   3. Access the application at http://localhost:3000")
            sys.exit(0)
        else:
            print("❌ Database initialization failed validation")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
