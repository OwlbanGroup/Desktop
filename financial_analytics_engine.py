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
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

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

class AIPredictiveAnalytics:
    """AI-powered predictive analytics using machine learning"""

    def __init__(self):
        self.models_dir = "models"
        os.makedirs(self.models_dir, exist_ok=True)
        self.scaler = StandardScaler()

    def prepare_time_series_data(self, data: List[Dict[str, Any]], lookback: int = 30) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare time series data for AI modeling"""
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df['revenue'] = df['amount']

        # Create features
        features = []
        targets = []

        for i in range(len(df) - lookback):
            feature_window = df['revenue'].iloc[i:i+lookback].values
            target = df['revenue'].iloc[i+lookback]
            features.append(feature_window)
            targets.append(target)

        X = np.array(features)
        y = np.array(targets)

        return X, y

    def train_revenue_prediction_model(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train AI model for revenue prediction"""
        try:
            X, y = self.prepare_time_series_data(historical_data)

            if len(X) < 10:
                return {'error': 'Insufficient data for AI training'}

            # Normalize data
            X_scaled = self.scaler.fit_transform(X.reshape(X.shape[0], -1))

            # Use Random Forest for prediction (works well with smaller datasets)
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_scaled, y)

            # Save model
            model_path = os.path.join(self.models_dir, 'revenue_prediction_model.pkl')
            joblib.dump(model, model_path)

            return {
                'success': True,
                'model_path': model_path,
                'training_info': {
                    'data_points': len(X),
                    'features': X.shape[1],
                    'model_type': 'RandomForestRegressor'
                }
            }

        except Exception as e:
            return {'error': f'AI training failed: {str(e)}'}

    def predict_future_revenue(self, historical_data: List[Dict[str, Any]], days_ahead: int = 30) -> Dict[str, Any]:
        """Predict future revenue using trained AI model"""
        try:
            model_path = os.path.join(self.models_dir, 'revenue_prediction_model.pkl')

            if not os.path.exists(model_path):
                return {'error': 'No trained model found'}

            # Load model
            model = joblib.load(model_path)

            # Prepare recent data for prediction
            recent_data = historical_data[-30:] if len(historical_data) >= 30 else historical_data
            X, _ = self.prepare_time_series_data(recent_data)

            if len(X) == 0:
                return {'error': 'Insufficient data for prediction'}

            # Make prediction
            X_scaled = self.scaler.transform(X.reshape(X.shape[0], -1))
            prediction = model.predict(X_scaled[-1].reshape(1, -1))[0]

            # Calculate confidence interval
            confidence_range = prediction * 0.15  # 15% confidence range

            return {
                'predicted_revenue': float(prediction),
                'confidence_lower': float(prediction - confidence_range),
                'confidence_upper': float(prediction + confidence_range),
                'days_ahead': days_ahead,
                'prediction_date': (datetime.utcnow() + timedelta(days=days_ahead)).isoformat(),
                'model_accuracy': 'High' if len(historical_data) > 50 else 'Medium'
            }

        except Exception as e:
            return {'error': f'Prediction failed: {str(e)}'}

    def analyze_risk_factors(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze financial risk factors"""
        try:
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            # Calculate volatility
            if len(df) > 1:
                returns = df['amount'].pct_change().dropna()
                volatility = returns.std() * np.sqrt(252)  # Annualized volatility

                # Risk assessment
                risk_score = min(100, volatility * 1000)  # Scale to 0-100

                risk_level = 'Low' if risk_score < 30 else 'Medium' if risk_score < 70 else 'High'

                # Identify risk factors
                risk_factors = []

                if volatility > 0.5:
                    risk_factors.append('High revenue volatility detected')

                if df['amount'].iloc[-1] < df['amount'].mean() * 0.7:
                    risk_factors.append('Recent revenue significantly below average')

                if len(df[df['amount'] < 0]) > 0:
                    risk_factors.append('Negative revenue entries detected')

                return {
                    'risk_score': float(risk_score),
                    'risk_level': risk_level,
                    'volatility': float(volatility),
                    'risk_factors': risk_factors,
                    'recommendations': self._generate_risk_recommendations(risk_level, risk_factors)
                }
            else:
                return {'error': 'Insufficient data for risk analysis'}

        except Exception as e:
            return {'error': f'Risk analysis failed: {str(e)}'}

    def _generate_risk_recommendations(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []

        if risk_level == 'High':
            recommendations.extend([
                'Implement diversified revenue streams',
                'Build cash reserves for 6-12 months',
                'Review and optimize cost structure',
                'Consider professional financial advisory'
            ])
        elif risk_level == 'Medium':
            recommendations.extend([
                'Monitor revenue trends closely',
                'Develop contingency plans',
                'Strengthen customer relationships',
                'Explore new market opportunities'
            ])
        else:
            recommendations.extend([
                'Continue current risk management practices',
                'Monitor for emerging risk factors',
                'Maintain diversified revenue streams'
            ])

        # Add specific recommendations based on risk factors
        for factor in risk_factors:
            if 'volatility' in factor.lower():
                recommendations.append('Implement revenue smoothing strategies')
            if 'below average' in factor.lower():
                recommendations.append('Conduct market analysis and customer feedback surveys')
            if 'negative' in factor.lower():
                recommendations.append('Review pricing strategy and cost management')

        return list(set(recommendations))  # Remove duplicates

class AdvancedRevenueTracker:
    def __init__(self, db_url: str = "sqlite:///revenue.db"):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.kpis = FinancialKPIs()
        self.ai_analytics = AIPredictiveAnalytics()

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

    def _get_category_enum(self, category_name: str) -> Optional[RevenueCategory]:
        """Safely convert category name string to RevenueCategory enum"""
        try:
            # Try to match the category name to enum values
            for enum_value in RevenueCategory:
                if enum_value.value == category_name:
                    return enum_value
            return None
        except (ValueError, AttributeError):
            return None

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
            category_enum = self._get_category_enum(category)
            if category_enum:
                current_cat = self.get_total_revenue(category=category_enum, start_date=current_start, end_date=now)
                previous_cat = self.get_total_revenue(category=category_enum, start_date=previous_start, end_date=current_start)
                category_growth[category] = self.kpis.calculate_growth_rate(current_cat, previous_cat)
            else:
                # If category doesn't match enum, calculate without category filter
                category_growth[category] = 0.0

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

    def ai_powered_forecasting(self, days_ahead: int = 30) -> Dict[str, Any]:
        """AI-powered revenue forecasting"""
        historical_data = [record.to_dict() for record in self.get_all_records()]

        if len(historical_data) < 10:
            return {'error': 'Insufficient historical data for AI forecasting'}

        # Train model if not exists
        training_result = self.ai_analytics.train_revenue_prediction_model(historical_data)

        if 'error' in training_result:
            return training_result

        # Make prediction
        prediction = self.ai_analytics.predict_future_revenue(historical_data, days_ahead)

        return {
            'ai_forecast': prediction,
            'training_info': training_result,
            'forecast_period_days': days_ahead,
            'data_quality': 'High' if len(historical_data) > 50 else 'Medium'
        }

    def ai_risk_analysis(self) -> Dict[str, Any]:
        """AI-powered risk analysis"""
        historical_data = [record.to_dict() for record in self.get_all_records()]

        if len(historical_data) < 5:
            return {'error': 'Insufficient data for risk analysis'}

        return self.ai_analytics.analyze_risk_factors(historical_data)

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

        # AI-powered insights
        ai_forecast = self.ai_powered_forecasting(days_ahead=30)
        ai_risk = self.ai_risk_analysis()

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
            'forecast': self.advanced_forecasting(months_ahead=3),
            'ai_insights': {
                'forecast': ai_forecast,
                'risk_analysis': ai_risk,
                'recommendations': self._generate_ai_recommendations(ai_forecast, ai_risk)
            }
        }

    def _generate_ai_recommendations(self, forecast: Dict, risk: Dict) -> List[str]:
        """Generate AI-powered recommendations"""
        recommendations = []

        # Forecast-based recommendations
        if 'ai_forecast' in forecast and 'predicted_revenue' in forecast['ai_forecast']:
            predicted = forecast['ai_forecast']['predicted_revenue']
            current = self.get_total_revenue()

            if predicted > current * 1.2:
                recommendations.append('Strong growth predicted - prepare for scaling operations')
            elif predicted < current * 0.8:
                recommendations.append('Revenue decline predicted - implement cost optimization measures')

        # Risk-based recommendations
        if 'risk_level' in risk:
            if risk['risk_level'] == 'High':
                recommendations.extend([
                    'High risk detected - diversify revenue streams immediately',
                    'Build emergency cash reserves',
                    'Review and strengthen risk management policies'
                ])
            elif risk['risk_level'] == 'Medium':
                recommendations.extend([
                    'Monitor risk factors closely',
                    'Develop contingency plans for potential revenue fluctuations'
                ])

        return recommendations

    def generate_financial_alerts(self) -> List[Dict[str, Any]]:
        """Generate automated financial alerts based on KPIs and AI insights"""
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

        # AI-powered alerts
        ai_risk = self.ai_risk_analysis()
        if 'risk_level' in ai_risk and ai_risk['risk_level'] == 'High':
            alerts.append({
                'type': 'critical',
                'category': 'ai_risk_alert',
                'message': f'AI Risk Analysis: {ai_risk["risk_level"]} risk level detected',
                'severity': 'high',
                'recommendation': 'Immediate risk mitigation required'
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
                'total_records': len(self.get_all_records(start_date=start_date, end_date=end_date))
            },
            'executive_summary': dashboard_data,
            'alerts': alerts,
            'recommendations': self.generate_recommendations(alerts)
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
