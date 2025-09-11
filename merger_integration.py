"""
Merger Analytics Integration Module
Provides comprehensive merger analysis capabilities for the financial dashboard
"""

from merger_analytics import MergerAnalytics
from datetime import datetime, timedelta
import json
import os

class MergerIntegration:
    """Integration class for merger analytics functionality"""

    def __init__(self):
        self.merger_analytics = MergerAnalytics()
        self.reports_dir = "merger_reports"
        os.makedirs(self.reports_dir, exist_ok=True)

    def get_merger_overview(self):
        """Get comprehensive merger overview"""
        try:
            # Generate current merger report
            report = self.merger_analytics.generate_comprehensive_report()

            return {
                'success': True,
                'data': {
                    'companies_involved': report.get('companies_involved', ['Oscar', 'Broome']),
                    'merger_date': report.get('merger_date', '2024-01-01'),
                    'current_status': 'Active Integration',
                    'integration_progress': self._calculate_integration_progress(),
                    'key_metrics': self._get_key_metrics(report),
                    'risk_assessment': report.get('risk_assessment', {}),
                    'recommendations': report.get('recommendations', [])
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_pre_merger_analysis(self):
        """Get pre-merger financial analysis"""
        try:
            analysis = self.merger_analytics.analyze_pre_merger_performance()
            return {
                'success': True,
                'data': analysis
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_synergy_analysis(self):
        """Get synergy analysis and projections"""
        try:
            synergies = self.merger_analytics.calculate_synergies()
            return {
                'success': True,
                'data': synergies
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_integration_costs(self):
        """Get integration cost projections"""
        try:
            costs = self.merger_analytics.project_integration_costs()
            return {
                'success': True,
                'data': costs
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_value_realization_timeline(self):
        """Get value realization timeline"""
        try:
            timeline = self.merger_analytics.project_value_realization()
            return {
                'success': True,
                'data': timeline
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_risk_assessment(self):
        """Get comprehensive risk assessment"""
        try:
            risks = self.merger_analytics.assess_risks()
            return {
                'success': True,
                'data': risks
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_post_merger_performance(self):
        """Get post-merger performance analysis"""
        try:
            performance = self.merger_analytics.monitor_post_merger_performance()
            return {
                'success': True,
                'data': performance
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def generate_executive_report(self, filename=None):
        """Generate executive merger report"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"merger_executive_report_{timestamp}.json"

            filepath = os.path.join(self.reports_dir, filename)
            report = self.merger_analytics.generate_comprehensive_report()

            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)

            return {
                'success': True,
                'message': f'Executive report generated: {filepath}',
                'filepath': filepath
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_merger_dashboard_data(self):
        """Get data for merger dashboard visualization"""
        try:
            report = self.merger_analytics.generate_comprehensive_report()

            dashboard_data = {
                'timeline': self._create_timeline_data(report),
                'financials': self._create_financial_data(report),
                'risks': self._create_risk_data(report),
                'synergies': self._create_synergy_data(report),
                'progress': self._calculate_integration_progress()
            }

            return {
                'success': True,
                'data': dashboard_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _calculate_integration_progress(self):
        """Calculate current integration progress percentage"""
        # This would be based on actual integration milestones
        # For now, return a sample progress
        return {
            'overall_progress': 75,
            'phases': {
                'planning': 100,
                'due_diligence': 100,
                'integration_setup': 80,
                'system_integration': 70,
                'cultural_alignment': 60,
                'performance_monitoring': 50
            },
            'milestones_completed': 12,
            'total_milestones': 16
        }

    def _get_key_metrics(self, report):
        """Extract key metrics from report"""
        pre_merger = report.get('pre_merger_performance', {})
        synergies = report.get('synergy_estimates', {})
        costs = report.get('integration_costs', {})

        oscar_revenue = pre_merger.get('Oscar', {}).get('total_revenue', 0)
        broome_revenue = pre_merger.get('Broome', {}).get('total_revenue', 0)
        total_synergies = synergies.get('total_synergies', 0)
        total_costs = costs.get('projected', 0)

        return {
            'combined_revenue': oscar_revenue + broome_revenue,
            'expected_synergies': total_synergies,
            'integration_costs': total_costs,
            'roi_percentage': (total_synergies / total_costs * 100) if total_costs > 0 else 0,
            'synergy_to_revenue_ratio': (total_synergies / (oscar_revenue + broome_revenue) * 100) if (oscar_revenue + broome_revenue) > 0 else 0
        }

    def _create_timeline_data(self, report):
        """Create timeline data for dashboard"""
        timeline = report.get('value_realization_timeline', {}).get('timeline', [])

        return {
            'labels': [f"Year {item['year']}" for item in timeline],
            'expected_benefits': [item['expected_benefit_percentage'] for item in timeline],
            'actual_benefits': [item['expected_benefit_percentage'] * 0.8 for item in timeline]  # Sample actual data
        }

    def _create_financial_data(self, report):
        """Create financial data for dashboard"""
        pre_merger = report.get('pre_merger_performance', {})
        synergies = report.get('synergy_estimates', {})

        return {
            'companies': ['Oscar', 'Broome'],
            'revenues': [
                pre_merger.get('Oscar', {}).get('total_revenue', 0),
                pre_merger.get('Broome', {}).get('total_revenue', 0)
            ],
            'synergies': {
                'cost_savings': synergies.get('cost_savings', 0),
                'revenue_enhancement': synergies.get('revenue_enhancement', 0),
                'total': synergies.get('total_synergies', 0)
            }
        }

    def _create_risk_data(self, report):
        """Create risk data for dashboard"""
        risks = report.get('risk_assessment', {}).get('risks', {})

        risk_levels = {
            'Low': 1,
            'Medium': 2,
            'High': 3
        }

        return {
            'categories': list(risks.keys()),
            'levels': [risk_levels.get(risks[category], 1) for category in risks.keys()],
            'colors': ['#28a745' if risks[category] == 'Low' else '#ffc107' if risks[category] == 'Medium' else '#dc3545' for category in risks.keys()]
        }

    def _create_synergy_data(self, report):
        """Create synergy data for dashboard"""
        synergies = report.get('synergy_estimates', {})

        return {
            'categories': ['Cost Savings', 'Revenue Enhancement'],
            'values': [
                synergies.get('cost_savings', 0),
                synergies.get('revenue_enhancement', 0)
            ],
            'total': synergies.get('total_synergies', 0)
        }

# Global instance for easy access
merger_integration = MergerIntegration()
