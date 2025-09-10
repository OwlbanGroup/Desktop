"""
Database Models for Owlban Group Integrated Platform
Provides SQLAlchemy models for all core entities
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(20), default='user')  # admin, manager, user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    leadership_sessions = relationship("LeadershipSession", back_populates="user")
    overrides = relationship("LoginOverride", back_populates="user")

class LeadershipSession(Base):
    """Leadership simulation session model"""
    __tablename__ = 'leadership_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    leader_name = Column(String(100), nullable=False)
    leadership_style = Column(String(20), nullable=False)
    team_members = Column(JSON, nullable=False)  # Store as JSON array
    lead_result = Column(Text)
    team_status = Column(JSON)  # Store team status as JSON
    revenue_impact = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="leadership_sessions")
    decisions = relationship("Decision", back_populates="session")

class Decision(Base):
    """Decision model for leadership decisions"""
    __tablename__ = 'decisions'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('leadership_sessions.id'), nullable=False)
    decision_text = Column(Text, nullable=False)
    decision_result = Column(Text)
    revenue_impact = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("LeadershipSession", back_populates="decisions")

class RevenueRecord(Base):
    """Revenue tracking model"""
    __tablename__ = 'revenue_records'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(200))
    category = Column(String(50))
    source = Column(String(50))
    recorded_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LoginOverride(Base):
    """Login override model for emergency access"""
    __tablename__ = 'login_overrides'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    override_type = Column(String(20), nullable=False)  # emergency, admin, technical
    reason = Column(String(100), nullable=False)
    justification = Column(Text)
    emergency_code = Column(String(100))  # For emergency overrides
    admin_user_id = Column(String(100))  # For admin overrides
    support_user_id = Column(String(100))  # For technical overrides
    ticket_number = Column(String(50))  # For technical overrides
    target_user_id = Column(String(100))  # Target user for override
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=False)

    # Relationships
    user = relationship("User", back_populates="overrides")

class AuditLog(Base):
    """Audit logging model"""
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=False)
    resource_id = Column(String(100))
    details = Column(JSON)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")

class SystemHealth(Base):
    """System health monitoring model"""
    __tablename__ = 'system_health'

    id = Column(Integer, primary_key=True)
    service_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)  # healthy, degraded, unhealthy
    response_time = Column(Float)  # in milliseconds
    error_message = Column(Text)
    metrics = Column(JSON)  # Additional health metrics
    checked_at = Column(DateTime, default=datetime.utcnow)

class PayrollRecord(Base):
    """Payroll integration model"""
    __tablename__ = 'payroll_records'

    id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), nullable=False)
    payroll_data = Column(JSON, nullable=False)  # Store QuickBooks payroll data
    sync_status = Column(String(20), default='pending')  # pending, synced, failed
    synced_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
