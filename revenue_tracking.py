"""
Revenue Tracking Module

This module provides basic functionality to track revenue data such as sales and payments,
store them in a SQLite database using SQLAlchemy, and generate simple reports.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class RevenueRecord(Base):
    __tablename__ = 'revenue_records'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RevenueRecord(id={self.id}, description='{self.description}', amount={self.amount}, date={self.date})>"

class RevenueTracker:
    def __init__(self, db_url: str = "sqlite:///revenue.db"):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_record(self, description: str, amount: float, date: Optional[datetime] = None) -> RevenueRecord:
        if amount < 0:
            raise ValueError("Amount must be non-negative")
        if not description:
            raise ValueError("Description must not be empty")
        session = self.Session()
        record = RevenueRecord(description=description, amount=amount, date=date or datetime.utcnow())
        session.add(record)
        session.commit()
        session.refresh(record)
        session.close()
        return record

    def get_all_records(self) -> List[RevenueRecord]:
        session = self.Session()
        records = session.query(RevenueRecord).order_by(RevenueRecord.date.desc()).all()
        session.close()
        return records

    def get_total_revenue(self) -> float:
        session = self.Session()
        total = session.query(func.sum(RevenueRecord.amount)).scalar() or 0.0
        session.close()
        return total

    def generate_report(self) -> str:
        records = self.get_all_records()
        report_lines = ["Revenue Report:"]
        for record in records:
            report_lines.append(f"{record.date.strftime('%Y-%m-%d %H:%M:%S')} - {record.description}: ${record.amount:.2f}")
        report_lines.append(f"Total Revenue: ${self.get_total_revenue():.2f}")
        return "\n".join(report_lines)
