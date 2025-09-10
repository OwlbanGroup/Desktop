"""
Enhanced Backend Server with Financial Excellence Integration

This server integrates advanced financial analytics, executive dashboards,
and comprehensive reporting capabilities for achieving financial excellence.
"""

from flask import Flask, send_from_directory, jsonify, request
import os
import subprocess
import requests
import sys
from datetime import datetime

# Add aeni ectAry to Pythondppah eodirectormoyultsofrop root import modules from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from organizational_leadership import leadership
from revenue_tracking import RevenueTracker
from nvidia_integration_fixed import NvidiaIntegration
from financial_analytics_engine import AdvancedRevenueTracker, RevenueCategory
from financial_dashboard import FinancialDashboard, FinancialExcellenceManager

app = Flask(__name__, static_folder='./frontend')

OSCAR_BROOME_URL = os.getenv('OSCAR_BROOME_URL', 'http://localhost:4000')

# Initialize components
revenue_tracker = RevenueTracker()
nvidia_integration = NvidiaIntegration()

# Initialize advanced financial components
advanced_tracker = AdvancedRevenueTracker()
financial_dashboard = FinancialDashboard(advanced_tracker)
excellence_manager = FinancialExcellenceManager(advanced_tracker)

# ===== FINANCIAL EXCELLENCE API ENDPOINTS =====

@app.route('/api/financial/executive-summary', methods=['GET'])
def get_executive_summary():
    """Get executive summary with key financial metrics"""
    try:
        period_days = int(request.args.get('period_days', 30))
        summary = financial_dashboard.get_executive_summary(period_days)
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/financial/dashboard', methods=['GET'])
def get_financial_dashboard():
    """Get comprehensive financial dashboard data"""
    try:
        period_days = int(request.args.get('period_days', 30))
        dashboard_data = financial_dashboard.generate_financial_report('comprehensive', period_days)
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/financial/performance-trends', methods=['GET'])
def get_performance_trends():
    """Get performance trends analysis"""
    try:
        months = int(request.args.get('months', 6))
        trends = financial_dashboard.get_performance_trends(months)
        return jsonify({
            'success': True,
            'data': trends
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/financial/category-analysis', methods=['GET'])
def get_category_analysis():
    """Get detailed category performance analysis"""
    try:
        period_days = int(request.args.get('period_days', 30))
        analysis = financial_dashboard.get_category_analysis(period_days)
        return jsonify({
            'success': True,
            'data': analysis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

