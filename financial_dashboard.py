"""
Financial Excellence Dashboard

This module provides comprehensive financial dashboards, executive reporting,
and real-time financial insights for achieving financial excellence.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import json
from collections import defaultdict
from financial_analytics_engine import AdvancedRevenueTracker, RevenueCategory
import statistics

class FinancialDashboard:
    """Executive financial dashboard with real-time insights"""

    def __init__(self, revenue_tracker: AdvancedRevenueTracker):
        self.tracker = revenue_tracker
        self.dashboard_cache = {}
        self.last_update = None

    def get_executive_summary(self, period_days: int = 30) -> Dict[str, Any]:
        """Generate executive summary with key financial metrics"""
        dashboard_data = self.tracker.generate_executive_dashboard(period_days)

        # Calculate health score
        health_score = self._calculate_financial_health_score(dashboard_data)

        # Generate insights
        insights = self._generate_executive_insights(dashboard_data)

        return {
            'health_score': health_score,
            'key_metrics': {
                'total_revenue': dashboard_data['summary_metrics']['total_revenue'],
                'growth_rate': dashboard_data['kpis']['growth_rate'],
                'total_transactions': dashboard_data['summary_metrics']['total_transactions'],
                'avg_transaction_value': dashboard_data['summary_metrics']['average_transaction_value']
            },
            'top_performers': dashboard_data['category_performance']['top_performers'],
            'insights': insights,
            'alerts': self.tracker.generate_financial_alerts(),
            'period': dashboard_data['period']
        }

    def _calculate_financial_health_score(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall financial health score (0-100)"""
        score = 0
        max_score = 100
        factors = []

        # Growth rate factor (30 points)
        growth_rate = dashboard_data['kpis']['growth_rate']
        if growth_rate >= 20:
            growth_score = 30
            growth_status = "Excellent"
        elif growth_rate >= 10:
            growth_score = 25
            growth_status = "Good"
        elif growth_rate >= 0:
            growth_score = 15
            growth_status = "Stable"
        elif growth_rate >= -10:
            growth_score = 5
            growth_status = "Declining"
        else:
            growth_score = 0
            growth_status = "Critical"

        score += growth_score
        factors.append({
            'factor': 'Revenue Growth',
            'score': growth_score,
            'max_score': 30,
            'status': growth_status,
            'value': f"{growth_rate:.1f}%"
        })

        # Transaction volume factor (20 points)
        transactions = dashboard_data['summary_metrics']['total_transactions']
        if transactions >= 100:
            transaction_score = 20
            transaction_status = "High Volume"
        elif transactions >= 50:
            transaction_score = 15
            transaction_status = "Moderate Volume"
        elif transactions >= 20:
            transaction_score = 10
            transaction_status = "Low Volume"
        else:
            transaction_score = 5
            transaction_status = "Very Low Volume"

        score += transaction_score
        factors.append({
            'factor': 'Transaction Volume',
            'score': transaction_score,
            'max_score': 20,
            'status': transaction_status,
            'value': f"{transactions} transactions"
        })

        # Revenue concentration factor (20 points)
        top_category_percentage = 0
        if dashboard_data['category_performance']['top_performers']:
            total_revenue = dashboard_data['summary_metrics']['total_revenue']
            top_category_revenue = dashboard_data['category_performance']['top_performers'][0][1]
            top_category_percentage = (top_category_revenue / total_revenue) * 100 if total_revenue > 0 else 0

        if top_category_percentage <= 40:
            concentration_score = 20
            concentration_status = "Well Diversified"
        elif top_category_percentage <= 60:
            concentration_score = 15
            concentration_status = "Moderately Diversified"
        elif top_category_percentage <= 80:
            concentration_score = 10
            concentration_status = "Concentrated"
        else:
            concentration_score = 5
            concentration_status = "High Risk"

        score += concentration_score
        factors.append({
            'factor': 'Revenue Diversification',
            'score': concentration_score,
            'max_score': 20,
            'status': concentration_status,
            'value': f"{top_category_percentage:.1f}% concentration"
        })

        # Average transaction value factor (15 points)
        avg_transaction = dashboard_data['summary_metrics']['average_transaction_value']
        if avg_transaction >= 500:
            avg_score = 15
            avg_status = "Premium"
        elif avg_transaction >= 200:
            avg_score = 12
            avg_status = "Good"
        elif avg_transaction >= 100:
            avg_score = 8
            avg_status = "Moderate"
        elif avg_transaction >= 50:
            avg_score = 5
            avg_status = "Low"
        else:
            avg_score = 2
            avg_status = "Very Low"

        score += avg_score
        factors.append({
            'factor': 'Transaction Value',
            'score': avg_score,
            'max_score': 15,
            'status': avg_status,
            'value': f"${avg_transaction:.2f}"
        })

        # Category count factor (15 points)
        category_count = dashboard_data['category_performance']['category_count']
        if category_count >= 5:
            category_score = 15
            category_status = "Excellent Diversification"
        elif category_count >= 3:
            category_score = 10
            category_status = "Good Diversification"
        elif category_count >= 2:
            category_score = 5
            category_status = "Basic Diversification"
        else:
            category_score = 0
            category_status = "Single Source"

        score += category_score
        factors.append({
            'factor': 'Revenue Streams',
            'score': category_score,
            'max_score': 15,
            'status': category_status,
            'value': f"{category_count} categories"
        })

        # Determine overall status
        if score >= 80:
            overall_status = "Excellent"
            color = "green"
        elif score >= 60:
            overall_status = "Good"
            color = "blue"
        elif score >= 40:
            overall_status = "Fair"
            color = "yellow"
        elif score >= 20:
            overall_status = "Poor"
            color = "orange"
        else:
            overall_status = "Critical"
            color = "red"

        return {
            'total_score': score,
            'max_score': max_score,
            'percentage': (score / max_score) * 100,
            'status': overall_status,
            'color': color,
            'factors': factors,
            'last_updated': datetime.utcnow().isoformat()
        }

    def _generate_executive_insights(self, dashboard_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable executive insights"""
        insights = []

        # Growth insights
        growth_rate = dashboard_data['kpis']['growth_rate']
        if growth_rate > 20:
            insights.append({
                'type': 'positive',
                'category': 'growth',
                'title': 'Strong Revenue Growth',
                'description': f'Revenue increased by {growth_rate:.1f}% - excellent performance!',
                'priority': 'high'
            })
        elif growth_rate < -10:
            insights.append({
                'type': 'negative',
                'category': 'growth',
                'title': 'Revenue Decline Alert',
                'description': f'Revenue decreased by {abs(growth_rate):.1f}% - requires immediate attention',
                'priority': 'critical'
            })

        # Transaction insights
        transactions = dashboard_data['summary_metrics']['total_transactions']
        if transactions < 20:
            insights.append({
                'type': 'warning',
                'category': 'volume',
                'title': 'Low Transaction Volume',
                'description': f'Only {transactions} transactions recorded - consider marketing initiatives',
                'priority': 'medium'
            })

        # Diversification insights
        category_count = dashboard_data['category_performance']['category_count']
        if category_count == 1:
            insights.append({
                'type': 'warning',
                'category': 'diversification',
                'title': 'Revenue Concentration Risk',
                'description': 'All revenue from single source - high business risk',
                'priority': 'high'
            })

        # Average transaction insights
        avg_transaction = dashboard_data['summary_metrics']['average_transaction_value']
        if avg_transaction > 500:
            insights.append({
                'type': 'positive',
                'category': 'value',
                'title': 'Premium Transaction Values',
                'description': f'Average transaction value of ${avg_transaction:.2f} indicates strong pricing power',
                'priority': 'medium'
            })

        return insights

    def get_performance_trends(self, months: int = 6) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        monthly_data = self.tracker.get_monthly_revenue(months=months)

        if len(monthly_data) < 2:
            return {'error': 'Insufficient data for trend analysis'}

        revenues = [data['total'] for data in monthly_data]

        # Calculate trend metrics
        trend_direction = "increasing" if revenues[-1] > revenues[0] else "decreasing"
        total_change = revenues[-1] - revenues[0]
        percentage_change = (total_change / revenues[0]) * 100 if revenues[0] > 0 else 0

        # Calculate volatility
        if len(revenues) > 1:
            volatility = statistics.stdev(revenues) / statistics.mean(revenues) if statistics.mean(revenues) > 0 else 0
        else:
            volatility = 0

        # Identify best and worst months
        best_month = max(monthly_data, key=lambda x: x['total'])
        worst_month = min(monthly_data, key=lambda x: x['total'])

        return {
            'trend_direction': trend_direction,
            'total_change': total_change,
            'percentage_change': percentage_change,
            'volatility': volatility,
            'best_month': best_month,
            'worst_month': worst_month,
            'monthly_data': monthly_data,
            'average_monthly_revenue': statistics.mean(revenues),
            'period_months': months
        }

    def get_category_analysis(self, period_days: int = 30) -> Dict[str, Any]:
        """Detailed category performance analysis"""
        start_date = datetime.utcnow() - timedelta(days=period_days)
        category_breakdown = self.tracker.get_revenue_by_category(start_date=start_date)

        if not category_breakdown:
            return {'error': 'No category data available'}

        total_revenue = sum(category_breakdown.values())

        # Calculate category metrics
        category_metrics = []
        for category, revenue in category_breakdown.items():
            percentage = (revenue / total_revenue) * 100

            # Get category trend (compare with previous period)
            prev_start = start_date - timedelta(days=period_days)
            prev_revenue = self.tracker.get_total_revenue(
                category=RevenueCategory(category),
                start_date=prev_start,
                end_date=start_date
            )

            growth_rate = ((revenue - prev_revenue) / prev_revenue) * 100 if prev_revenue > 0 else 0

            category_metrics.append({
                'category': category,
                'revenue': revenue,
                'percentage': percentage,
                'growth_rate': growth_rate,
                'trend': 'up' if growth_rate > 0 else 'down',
                'contribution': 'high' if percentage > 30 else 'medium' if percentage > 15 else 'low'
            })

        # Sort by revenue
        category_metrics.sort(key=lambda x: x['revenue'], reverse=True)

        return {
            'total_categories': len(category_metrics),
            'total_revenue': total_revenue,
            'category_metrics': category_metrics,
            'period_days': period_days,
            'analysis_date': datetime.utcnow().isoformat()
        }

    def generate_financial_report(self, report_type: str = 'comprehensive',
                                period_days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive financial report"""
        report = {
            'report_type': report_type,
            'generated_at': datetime.utcnow().isoformat(),
            'period_days': period_days
        }

        if report_type == 'comprehensive':
            report.update({
                'executive_summary': self.get_executive_summary(period_days),
                'performance_trends': self.get_performance_trends(),
                'category_analysis': self.get_category_analysis(period_days),
                'forecast': self.tracker.advanced_forecasting(),
                'alerts': self.tracker.generate_financial_alerts(),
                'recommendations': self.tracker.generate_recommendations(
                    self.tracker.generate_financial_alerts()
                )
            })
        elif report_type == 'summary':
            report.update({
                'executive_summary': self.get_executive_summary(period_days),
                'alerts': self.tracker.generate_financial_alerts()
            })
        elif report_type == 'trends':
            report.update({
                'performance_trends': self.get_performance_trends(),
                'forecast': self.tracker.advanced_forecasting()
            })

        return report

    def export_dashboard_data(self, filename: str, format: str = 'json') -> str:
        """Export dashboard data for external analysis"""
        dashboard_data = {
            'executive_summary': self.get_executive_summary(),
            'performance_trends': self.get_performance_trends(),
            'category_analysis': self.get_category_analysis(),
            'alerts': self.tracker.generate_financial_alerts(),
            'export_timestamp': datetime.utcnow().isoformat()
        }

        if format == 'json':
            with open(filename, 'w') as f:
                json.dump(dashboard_data, f, indent=2, default=str)
        elif format == 'csv':
            # Export key metrics to CSV
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value', 'Status'])

                summary = dashboard_data['executive_summary']
                writer.writerow(['Health Score', summary['health_score']['total_score'], summary['health_score']['status']])
                writer.writerow(['Total Revenue', summary['key_metrics']['total_revenue'], ''])
                writer.writerow(['Growth Rate', f"{summary['key_metrics']['growth_rate']:.1f}%", ''])
                writer.writerow(['Total Transactions', summary['key_metrics']['total_transactions'], ''])

        return f"Dashboard data exported to {filename} in {format} format"

class FinancialExcellenceManager:
    """Manager class for achieving financial excellence"""

    def __init__(self, revenue_tracker: AdvancedRevenueTracker):
        self.tracker = revenue_tracker
        self.dashboard = FinancialDashboard(revenue_tracker)

    def get_excellence_scorecard(self) -> Dict[str, Any]:
        """Generate comprehensive financial excellence scorecard"""
        summary = self.dashboard.get_executive_summary()
        trends = self.dashboard.get_performance_trends()
        categories = self.dashboard.get_category_analysis()

        # Calculate excellence metrics
        excellence_metrics = self._calculate_excellence_metrics(summary, trends, categories)

        return {
            'overall_excellence_score': excellence_metrics['overall_score'],
            'scorecard': excellence_metrics,
            'achievements': excellence_metrics['achievements'],
            'improvement_areas': excellence_metrics['improvement_areas'],
            'next_steps': excellence_metrics['next_steps'],
            'generated_at': datetime.utcnow().isoformat()
        }

    def _calculate_excellence_metrics(self, summary: Dict, trends: Dict, categories: Dict) -> Dict[str, Any]:
        """Calculate detailed excellence metrics"""
        metrics = {
            'overall_score': 0,
            'max_score': 100,
            'achievements': [],
            'improvement_areas': [],
            'next_steps': []
        }

        # Health score contribution (40 points)
        health_score = summary['health_score']['total_score']
        metrics['overall_score'] += health_score * 0.4

        if health_score >= 80:
            metrics['achievements'].append("Excellent financial health")
        elif health_score < 40:
            metrics['improvement_areas'].append("Financial health needs improvement")

        # Growth excellence (30 points)
        growth_rate = summary['key_metrics']['growth_rate']
        if growth_rate >= 20:
            metrics['overall_score'] += 30
            metrics['achievements'].append("Outstanding revenue growth")
        elif growth_rate >= 10:
            metrics['overall_score'] += 20
            metrics['achievements'].append("Strong revenue growth")
        elif growth_rate >= 0:
            metrics['overall_score'] += 10
            metrics['improvement_areas'].append("Growth rate could be improved")
        else:
            metrics['next_steps'].append("Implement growth strategies")

        # Diversification excellence (20 points)
        category_count = categories.get('total_categories', 0)
        if category_count >= 5:
            metrics['overall_score'] += 20
            metrics['achievements'].append("Excellent revenue diversification")
        elif category_count >= 3:
            metrics['overall_score'] += 15
            metrics['achievements'].append("Good revenue diversification")
        elif category_count >= 2:
            metrics['overall_score'] += 10
        else:
            metrics['improvement_areas'].append("Revenue diversification needed")

        # Volume excellence (10 points)
        transactions = summary['key_metrics']['total_transactions']
        if transactions >= 100:
            metrics['overall_score'] += 10
            metrics['achievements'].append("High transaction volume")
        elif transactions >= 50:
            metrics['overall_score'] += 7
        elif transactions >= 20:
            metrics['overall_score'] += 4

        # Generate next steps based on scores
        if metrics['overall_score'] >= 80:
            metrics['next_steps'].extend([
                "Maintain current excellent performance",
                "Explore expansion opportunities",
                "Implement advanced analytics"
            ])
        elif metrics['overall_score'] >= 60:
            metrics['next_steps'].extend([
                "Focus on growth acceleration",
                "Improve diversification",
                "Enhance customer acquisition"
            ])
        else:
            metrics['next_steps'].extend([
                "Conduct comprehensive financial review",
                "Develop recovery strategy",
                "Seek expert financial consultation"
            ])

        return metrics

    def generate_excellence_report(self, filename: str) -> str:
        """Generate comprehensive financial excellence report"""
        scorecard = self.get_excellence_scorecard()
        dashboard_data = self.dashboard.generate_financial_report()

        excellence_report = {
            'title': 'Financial Excellence Report',
            'generated_at': datetime.utcnow().isoformat(),
            'scorecard': scorecard,
            'dashboard_data': dashboard_data,
            'recommendations': self._generate_excellence_recommendations(scorecard)
        }

        with open(filename, 'w') as f:
            json.dump(excellence_report, f, indent=2, default=str)

        return f"Financial excellence report generated: {filename}"

    def _generate_excellence_recommendations(self, scorecard: Dict) -> List[str]:
        """Generate excellence-focused recommendations"""
        recommendations = []

        score = scorecard['overall_score']

        if score >= 80:
            recommendations.extend([
                "Continue implementing best practices",
                "Explore advanced financial technologies",
                "Consider strategic acquisitions or partnerships",
                "Develop comprehensive succession planning",
                "Invest in employee development and retention"
            ])
        elif score >= 60:
            recommendations.extend([
                "Implement targeted improvement initiatives",
                "Enhance financial reporting and analytics",
                "Develop comprehensive marketing strategies",
                "Strengthen customer relationship management",
                "Optimize operational efficiency"
            ])
        else:
            recommendations.extend([
                "Conduct thorough financial health assessment",
                "Develop comprehensive turnaround strategy",
                "Seek professional financial advisory services",
                "Implement strict cost control measures",
                "Focus on core business strengths"
            ])

        return recommendations
