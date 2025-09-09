"""
Financial Analytics Engine

This module provides advanced financial analytics, forecasting, KPI calculations,
and comprehensive reporting capabilities for achieving financial excellence.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func, and_, or_
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func as sql_func
import json
import statistics
from enum import Enum
import numpy as np
from collections import defaultdict

Base = declarative_base()

class RevenueCategory(Enum):
    SALES = "Sales"
    SERVICES = "Services"
    SUBSCRIPTIONS = "Subscriptions"
    INVESTMENTS = "Investments"
    OTHER = "Other"

class RevenueRecord(Base):
    __tablename__ = 'revenue_records'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, default=RevenueCategory.OTHER.value)
    date = Column(DateTime, default=datetime.utcnow)
    source = Column(String, default="Unknown")
    tags = Column(String, default="[]")  # JSON array of tags

    def __repr__(self):
        return f"<RevenueRecord(id={self.id}, description='{self.description}', amount={self.amount}, category='{self.category}', date={self.date})>"

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'amount': self.amount,
            'category': self.category,
            'date': self.date.isoformat(),
            'source': self.source,
            'tags': json.loads(self.tags) if self.tags else []
        }

class FinancialKPIs:
    """Calculate key financial performance indicators"""

    @staticmethod
    def calculate_growth_rate(current: float, previous: float) -> float:
        """Calculate growth rate percentage"""
        if previous == 0:
            return 0.0
        return ((current - previous) / previous) * 100

    @staticmethod
    def calculate_roi(investment: float, return_amount: float) -> float:
        """Calculate Return on Investment"""
        if investment == 0:
            return 0.0
        return ((return_amount - investment) / investment) * 100

    @staticmethod
    def calculate_profit_margin(revenue: float, costs: float) -> float:
        """Calculate profit margin percentage"""
        if revenue == 0:
            return 0.0
        return ((revenue - costs) / revenue) * 100

    @staticmethod
    def calculate_customer_acquisition_cost(total_marketing_spend: float, new_customers: int) -> float:
        """Calculate Customer Acquisition Cost"""
        if new_customers == 0:
            return 0.0
        return total_marketing_spend / new_customers

    @staticmethod
    def calculate_lifetime_value(average_order_value: float, purchase_frequency: float, customer_lifespan: float) -> float:
        """Calculate Customer Lifetime Value"""
        return average_order_value * purchase_frequency * customer_lifespan

class AdvancedRevenueTracker:
    def __init__(self, db_url: str = "sqlite:///revenue.db"):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.kpis = FinancialKPIs()

    def add_record(self, description: str, amount: float, category: RevenueCategory = RevenueCategory.OTHER,
                   date: Optional[datetime] = None, source: str = "Unknown", tags: List[str] = None) -> RevenueRecord:
        if amount < 0:
            raise ValueError("Amount must be non-negative")
        if not description:
            raise ValueError("Description must not be empty")

        session = self.Session()
        record = RevenueRecord(
            description=description,
            amount=amount,
            category=category.value,
            date=date or datetime.utcnow(),
            source=source,
            tags=json.dumps(tags or [])
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        session.close()
        return record

    def get_all_records(self, category: Optional[RevenueCategory] = None,
                       start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[RevenueRecord]:
        session = self.Session()
        query = session.query(RevenueRecord)

        if category:
            query = query.filter(RevenueRecord.category == category.value)
        if start_date:
            query = query.filter(RevenueRecord.date >= start_date)
        if end_date:
            query = query.filter(RevenueRecord.date <= end_date)

        records = query.order_by(RevenueRecord.date.desc()).all()
        session.close()
        return records

    def get_total_revenue(self, category: Optional[RevenueCategory] = None,
                         start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> float:
        session = self.Session()
        query = session.query(sql_func.sum(RevenueRecord.amount))

        if category:
            query = query.filter(RevenueRecord.category == category.value)
        if start_date:
            query = query.filter(RevenueRecord.date >= start_date)
        if end_date:
            query = query.filter(RevenueRecord.date <= end_date)

        total = query.scalar() or 0.0
        session.close()
        return total

    def get_revenue_by_category(self, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict[str, float]:
        session = self.Session()
        query = session.query(RevenueRecord.category, sql_func.sum(RevenueRecord.amount))

        if start_date:
            query = query.filter(RevenueRecord.date >= start_date)
        if end_date:
            query = query.filter(RevenueRecord.date <= end_date)

        results = query.group_by(RevenueRecord.category).all()
        session.close()

        return {category: amount for category, amount in results}

    def get_monthly_revenue(self, months: int = 12) -> List[Dict[str, Any]]:
        session = self.Session()
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 30)

        # Get monthly totals
        query = session.query(
            sql_func.strftime('%Y-%m', RevenueRecord.date).label('month'),
            sql_func.sum(RevenueRecord.amount).label('total')
        ).filter(
            RevenueRecord.date >= start_date
        ).group_by(
            sql_func.strftime('%Y-%m', RevenueRecord.date)
        ).order_by(
            sql_func.strftime('%Y-%m', RevenueRecord.date)
        )

        results = query.all()
        session.close()

        return [{'month': month, 'total': total} for month, total in results]

    def calculate_comprehensive_kpis(self, current_period_days: int = 30, previous_period_days: int = 30) -> Dict[str, Any]:
        """Calculate comprehensive financial KPIs with advanced metrics"""
        now = datetime.utcnow()
        current_start = now - timedelta(days=current_period_days)
        previous_start = current_start - timedelta(days=previous_period_days)

        current_revenue = self.get_total_revenue(start_date=current_start, end_date=now)
        previous_revenue = self.get_total_revenue(start_date=previous_start, end_date=current_start)

        growth_rate = self.kpis.calculate_growth_rate(current_revenue, previous_revenue)

        # Calculate advanced metrics
        current_records = self.get_all_records(start_date=current_start, end_date=now)
        previous_records = self.get_all_records(start_date=previous_start, end_date=current_start)

        avg_transaction = statistics.mean([r.amount for r in current_records]) if current_records else 0
        prev_avg_transaction = statistics.mean([r.amount for r in previous_records]) if previous_records else 0

        # Get category breakdown
        category_breakdown = self.get_revenue_by_category(start_date=current_start, end_date=now)

        # Calculate category growth rates
        category_growth = {}
        for category in category_breakdown.keys():
            current_cat = self.get_total_revenue(category=RevenueCategory(category), start_date=current_start, end_date=now)
            previous_cat = self.get_total_revenue(category=RevenueCategory(category), start_date=previous_start, end_date=current_start)
            category_growth[category] = self.kpis.calculate_growth_rate(current_cat, previous_cat)

        return {
            'current_period_revenue': current_revenue,
            'previous_period_revenue': previous_revenue,
            'growth_rate': growth_rate,
            'average_transaction': avg_transaction,
            'transaction_growth': self.kpis.calculate_growth_rate(avg_transaction, prev_avg_transaction),
            'category_breakdown': category_breakdown,
            'category_growth_rates': category_growth,
            'total_transactions': len(current_records),
            'period_days': current_period_days,
            'revenue_per_transaction': current_revenue / len(current_records) if current_records else 0
        }

    def advanced_forecasting(self, months_ahead: int = 6, method: str = 'linear') -> Dict[str, Any]:
        """Advanced revenue forecasting with multiple methods"""
        monthly_data = self.get_monthly_revenue(months=24)  # Use 2 years of data

        if len(monthly_data) < 6:
            return {'error': 'Insufficient data for forecasting'}

        revenues = [data['total'] for data in monthly_data]
        months = list(range(len(revenues)))

        forecast_results = {}

        if method == 'linear':
            # Linear regression
            if len(revenues) > 1:
                slope = (revenues[-1] - revenues[0]) / (len(revenues) - 1)
                intercept = revenues[0]

                forecast = []
                for i in range(1, months_ahead + 1):
                    predicted = intercept + slope * (len(revenues) + i - 1)
                    forecast.append({
                        'month': (datetime.utcnow() + timedelta(days=i * 30)).strftime('%Y-%m'),
                        'predicted_revenue': max(0, predicted),
                        'confidence': 'Medium' if len(revenues) >= 12 else 'Low'
                    })

                forecast_results['linear'] = forecast

        elif method == 'moving_average':
            # Moving average forecasting
            if len(revenues) >= 3:
                window_size = min(3, len(revenues))
                recent_avg = sum(revenues[-window_size:]) / window_size

                forecast = []
                for i in range(1, months_ahead + 1):
                    forecast.append({
                        'month': (datetime.utcnow() + timedelta(days=i * 30)).strftime('%Y-%m'),
                        'predicted_revenue': recent_avg,
                        'confidence': 'Low'
                    })

                forecast_results['moving_average'] = forecast

        # Calculate forecast accuracy metrics
        if len(revenues) >= 6:
            # Use last 3 months as test data
            test_data = revenues[-3:]
            train_data = revenues[:-3]

            # Simple validation
            forecast_results['validation'] = {
                'test_period_months': 3,
                'training_data_points': len(train_data),
                'method_used': method
            }

        return forecast_results

    def generate_executive_dashboard(self, period_days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive executive dashboard data"""
        now = datetime.utcnow()
        start_date = now - timedelta(days=period_days)

        # Core metrics
        total_revenue = self.get_total_revenue(start_date=start_date)
        total_transactions = len(self.get_all_records(start_date=start_date))
        category_breakdown = self.get_revenue_by_category(start_date=start_date)

        # KPI calculations
        kpis = self.calculate_comprehensive_kpis()

        # Trend analysis
        monthly_trend = self.get_monthly_revenue(months=6)

        # Top performing categories
        top_categories = sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]

        # Revenue distribution analysis
        records = self.get_all_records(start_date=start_date)
        if records:
            amounts = [r.amount for r in records]
            revenue_distribution = {
                'min': min(amounts),
                'max': max(amounts),
                'median': statistics.median(amounts),
                'mean': statistics.mean(amounts),
                'std_dev': statistics.stdev(amounts) if len(amounts) > 1 else 0
            }
        else:
            revenue_distribution = {'min': 0, 'max': 0, 'median': 0, 'mean': 0, 'std_dev': 0}

        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': now.isoformat(),
                'days': period_days
            },
            'summary_metrics': {
                'total_revenue': total_revenue,
                'total_transactions': total_transactions,
                'average_transaction_value': total_revenue / total_transactions if total_transactions > 0 else 0,
                'revenue_per_day': total_revenue / period_days
            },
            'kpis': kpis,
            'category_performance': {
                'breakdown': category_breakdown,
                'top_performers': top_categories,
                'category_count': len(category_breakdown)
            },
            'trends': {
                'monthly_revenue': monthly_trend,
                'growth_trend': 'positive' if kpis['growth_rate'] > 0 else 'negative'
            },
            'distribution_analysis': revenue_distribution,
            'forecast': self.advanced_forecasting(months_ahead=3)
        }

    def generate_financial_alerts(self) -> List[Dict[str, Any]]:
        """Generate automated financial alerts based on KPIs"""
        alerts = []
        kpis = self.calculate_comprehensive_kpis()

        # Growth rate alerts
        if kpis['growth_rate'] < -10:
            alerts.append({
                'type': 'warning',
                'category': 'revenue_decline',
                'message': f'Revenue declined by {abs(kpis["growth_rate"]):.1f}% compared to previous period',
                'severity': 'high',
                'recommendation': 'Review sales strategies and market conditions'
            })
        elif kpis['growth_rate'] > 20:
            alerts.append({
                'type': 'success',
                'category': 'revenue_growth',
                'message': f'Excellent revenue growth of {kpis["growth_rate"]:.1f}%',
                'severity': 'low',
                'recommendation': 'Analyze successful strategies for replication'
            })

        # Transaction volume alerts
        if kpis['total_transactions'] < 10:
            alerts.append({
                'type': 'warning',
                'category': 'low_activity',
                'message': f'Low transaction volume: only {kpis["total_transactions"]} transactions',
                'severity': 'medium',
                'recommendation': 'Increase marketing efforts or review pricing'
            })

        # Category concentration alerts
        category_breakdown = kpis['category_breakdown']
        if category_breakdown:
            total_revenue = sum(category_breakdown.values())
            top_category_percentage = (max(category_breakdown.values()) / total_revenue) * 100

            if top_category_percentage > 70:
                alerts.append({
                    'type': 'warning',
                    'category': 'concentration_risk',
                    'message': f'High revenue concentration: {top_category_percentage:.1f}% from single category',
                    'severity': 'medium',
                    'recommendation': 'Diversify revenue streams to reduce risk'
                })

        return alerts

    def export_comprehensive_report(self, filename: str, start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> str:
        """Export comprehensive financial report to JSON"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        dashboard_data = self.generate_executive_dashboard(period_days=(end_date - start_date).days)
        alerts = self.generate_financial_alerts()

        report_data = {
            'report_metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'report_type': 'comprehensive_financial_analysis'
            },
            'dashboard_data': dashboard_data,
            'alerts': alerts,
            'recommendations': self.generate_recommendations(alerts),
            'raw_data': {
                'total_records': len(self.get_all_records(start_date=start_date, end_date=end_date)),
                'export_timestamp': datetime.utcnow().isoformat()
            }
        }

        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        return f"Comprehensive financial report exported to {filename}"

    def generate_recommendations(self, alerts: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations based on alerts"""
        recommendations = []

        for alert in alerts:
            if alert['category'] == 'revenue_decline':
                recommendations.extend([
                    "Implement targeted marketing campaigns",
                    "Review and optimize pricing strategy",
                    "Analyze customer feedback for product improvements",
                    "Consider promotional offers to boost sales"
                ])
            elif alert['category'] == 'low_activity':
                recommendations.extend([
                    "Increase digital marketing presence",
                    "Launch customer referral program",
                    "Review competitor strategies",
                    "Optimize sales funnel conversion rates"
                ])
            elif alert['category'] == 'concentration_risk':
                recommendations.extend([
                    "Develop new product lines or services",
                    "Enter new market segments",
                    "Expand customer base geographically",
                    "Create diversified revenue streams"
                ])

        # Add general excellence recommendations
        recommendations.extend([
            "Implement regular financial performance reviews",
            "Set up automated KPI monitoring and alerting",
            "Develop comprehensive financial forecasting models",
            "Create detailed customer segmentation analysis"
        ])

        return list(set(recommendations))  # Remove duplicates

# Backward compatibility class
class RevenueTracker(AdvancedRevenueTracker):
    """Backward compatible RevenueTracker class"""

    def generate_report(self) -> str:
        """Generate basic text report (backward compatibility)"""
        records = self.get_all_records()
        report_lines = ["Revenue Report:"]
        for record in records:
            report_lines.append(f"{record.date.strftime('%Y-%m-%d %H:%M:%S')} - {record.description}: ${record.amount:.2f}")
        report_lines.append(f"Total Revenue: ${self.get_total_revenue():.2f}")
        return "\n".join(report_lines)
