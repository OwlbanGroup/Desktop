"""
Financial Excellence Backend API

A comprehensive Flask-based backend API that integrates advanced financial analytics,
AI-powered insights, risk assessment, and real-time monitoring for achieving financial excellence.
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import threading
import time
from datetime import datetime, timedelta
import logging
from financial_analytics_engine import AdvancedRevenueTracker, RevenueCategory
from financial_dashboard import FinancialDashboard, FinancialExcellenceManager
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize the financial analytics engine
tracker = AdvancedRevenueTracker()

# Initialize dashboard and excellence manager
dashboard = FinancialDashboard(tracker)
excellence_manager = FinancialExcellenceManager(tracker)

# Sample data for demonstration
def initialize_sample_data():
    """Initialize sample data for demonstration purposes"""
    try:
        # Check if data already exists
        existing_records = tracker.get_all_records()
        if len(existing_records) > 0:
            logger.info(f"Found {len(existing_records)} existing records")
            return

        # Add sample revenue data
        sample_data = [
            ("Q1 Sales Revenue", 150000, RevenueCategory.SALES, datetime.utcnow() - timedelta(days=90)),
            ("Service Contracts", 75000, RevenueCategory.SERVICES, datetime.utcnow() - timedelta(days=85)),
            ("Subscription Revenue", 45000, RevenueCategory.SUBSCRIPTIONS, datetime.utcnow() - timedelta(days=80)),
            ("Investment Returns", 25000, RevenueCategory.INVESTMENTS, datetime.utcnow() - timedelta(days=75)),
            ("Q2 Sales Revenue", 180000, RevenueCategory.SALES, datetime.utcnow() - timedelta(days=60)),
            ("Service Contracts Q2", 82000, RevenueCategory.SERVICES, datetime.utcnow() - timedelta(days=55)),
            ("Subscription Revenue Q2", 52000, RevenueCategory.SUBSCRIPTIONS, datetime.utcnow() - timedelta(days=50)),
            ("Investment Returns Q2", 18000, RevenueCategory.INVESTMENTS, datetime.utcnow() - timedelta(days=45)),
            ("Q3 Sales Revenue", 210000, RevenueCategory.SALES, datetime.utcnow() - timedelta(days=30)),
            ("Service Contracts Q3", 95000, RevenueCategory.SERVICES, datetime.utcnow() - timedelta(days=25)),
            ("Subscription Revenue Q3", 58000, RevenueCategory.SUBSCRIPTIONS, datetime.utcnow() - timedelta(days=20)),
            ("Investment Returns Q3", 32000, RevenueCategory.INVESTMENTS, datetime.utcnow() - timedelta(days=15)),
            ("Q4 Sales Revenue", 250000, RevenueCategory.SALES, datetime.utcnow() - timedelta(days=5)),
            ("Service Contracts Q4", 110000, RevenueCategory.SERVICES, datetime.utcnow() - timedelta(days=3)),
            ("Subscription Revenue Q4", 65000, RevenueCategory.SUBSCRIPTIONS, datetime.utcnow() - timedelta(days=2)),
            ("Investment Returns Q4", 28000, RevenueCategory.INVESTMENTS, datetime.utcnow() - timedelta(days=1)),
        ]

        for description, amount, category, date in sample_data:
            tracker.add_record(
                description=description,
                amount=amount,
                category=category,
                date=date,
                source="Sample Data"
            )

        logger.info("Sample data initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing sample data: {str(e)}")

# Real-time monitoring thread
def real_time_monitoring():
    """Background thread for real-time financial monitoring"""
    while True:
        try:
            # Generate alerts
            alerts = tracker.generate_financial_alerts()

            # Send alerts to connected clients
            if alerts:
                socketio.emit('financial_alerts', {'alerts': alerts})

            # Send real-time metrics
            dashboard_data = tracker.generate_executive_dashboard(period_days=30)
            socketio.emit('dashboard_update', dashboard_data)

            # Send excellence scorecard updates
            excellence_data = excellence_manager.get_excellence_scorecard()
            socketio.emit('excellence_update', excellence_data)

            # Sleep for 30 seconds
            time.sleep(30)

        except Exception as e:
            logger.error(f"Error in real-time monitoring: {str(e)}")
            time.sleep(30)

# API Routes
@app.route('/')
def index():
    """Serve the main dashboard"""
    return render_template('dashboard.html')

@app.route('/financial-excellence')
def financial_excellence_dashboard():
    """Serve the financial excellence dashboard"""
    return render_template('financial_excellence.html')

@app.route('/api/dashboard')
def get_dashboard():
    """Get comprehensive dashboard data"""
    try:
        period_days = int(request.args.get('period', 30))
        dashboard_data = tracker.generate_executive_dashboard(period_days=period_days)
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/excellence-dashboard')
def get_excellence_dashboard():
    """Get financial excellence dashboard data"""
    try:
        executive_summary = dashboard.get_executive_summary()
        performance_trends = dashboard.get_performance_trends()
        category_analysis = dashboard.get_category_analysis()
        excellence_scorecard = excellence_manager.get_excellence_scorecard()

        return jsonify({
            'executive_summary': executive_summary,
            'performance_trends': performance_trends,
            'category_analysis': category_analysis,
            'excellence_scorecard': excellence_scorecard
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/excellence-scorecard')
def get_excellence_scorecard():
    """Get financial excellence scorecard"""
    try:
        scorecard = excellence_manager.get_excellence_scorecard()
        return jsonify(scorecard)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/kpis')
def get_kpis():
    """Get key performance indicators"""
    try:
        kpis = tracker.calculate_comprehensive_kpis()
        return jsonify(kpis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/forecast')
def get_forecast():
    """Get revenue forecast"""
    try:
        months_ahead = int(request.args.get('months', 6))
        forecast = tracker.advanced_forecasting(months_ahead=months_ahead)
        return jsonify(forecast)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-forecast')
def get_ai_forecast():
    """Get AI-powered forecast"""
    try:
        days_ahead = int(request.args.get('days', 30))
        forecast = tracker.ai_powered_forecasting(days_ahead=days_ahead)
        return jsonify(forecast)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/risk-analysis')
def get_risk_analysis():
    """Get AI-powered risk analysis"""
    try:
        risk_analysis = tracker.ai_risk_analysis()
        return jsonify(risk_analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts')
def get_alerts():
    """Get financial alerts"""
    try:
        alerts = tracker.generate_financial_alerts()
        return jsonify({'alerts': alerts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance-trends')
def get_performance_trends():
    """Get performance trends analysis"""
    try:
        months = int(request.args.get('months', 6))
        trends = dashboard.get_performance_trends(months=months)
        return jsonify(trends)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/category-analysis')
def get_category_analysis():
    """Get category performance analysis"""
    try:
        period_days = int(request.args.get('period', 30))
        analysis = dashboard.get_category_analysis(period_days=period_days)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/revenue', methods=['GET', 'POST'])
def revenue_operations():
    """Revenue CRUD operations"""
    if request.method == 'POST':
        try:
            data = request.get_json()

            record = tracker.add_record(
                description=data['description'],
                amount=data['amount'],
                category=RevenueCategory(data['category']),
                source=data.get('source', 'API'),
                tags=data.get('tags', [])
            )

            return jsonify({'success': True, 'record': record.to_dict()})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    else:
        try:
            category = request.args.get('category')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')

            if start_date:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if end_date:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

            records = tracker.get_all_records(
                category=RevenueCategory(category) if category else None,
                start_date=start_date,
                end_date=end_date
            )

            return jsonify({'records': [record.to_dict() for record in records]})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/revenue/<int:record_id>', methods=['PUT', 'DELETE'])
def revenue_record_operations(record_id):
    """Update or delete revenue record"""
    if request.method == 'PUT':
        try:
            data = request.get_json()
            # Note: In a real implementation, you'd need to add update methods to the tracker
            return jsonify({'success': True, 'message': 'Update functionality to be implemented'})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    elif request.method == 'DELETE':
        try:
            # Note: In a real implementation, you'd need to add delete methods to the tracker
            return jsonify({'success': True, 'message': 'Delete functionality to be implemented'})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

@app.route('/api/categories')
def get_categories():
    """Get revenue categories breakdown"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        categories = tracker.get_revenue_by_category(start_date=start_date, end_date=end_date)
        return jsonify({'categories': categories})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/monthly-trend')
def get_monthly_trend():
    """Get monthly revenue trend"""
    try:
        months = int(request.args.get('months', 12))
        trend = tracker.get_monthly_revenue(months=months)
        return jsonify({'trend': trend})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/total-revenue')
def get_total_revenue():
    """Get total revenue with optional filters"""
    try:
        category = request.args.get('category')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        total = tracker.get_total_revenue(
            category=RevenueCategory(category) if category else None,
            start_date=start_date,
            end_date=end_date
        )

        return jsonify({'total_revenue': total})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('connected', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

@socketio.on('request_dashboard_update')
def handle_dashboard_request():
    """Handle request for dashboard update"""
    try:
        dashboard_data = tracker.generate_executive_dashboard()
        emit('dashboard_update', dashboard_data)
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('request_excellence_update')
def handle_excellence_request():
    """Handle request for excellence dashboard update"""
    try:
        excellence_data = excellence_manager.get_excellence_scorecard()
        emit('excellence_update', excellence_data)
    except Exception as e:
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    # Initialize sample data
    initialize_sample_data()

    # Start real-time monitoring in background thread
    monitoring_thread = threading.Thread(target=real_time_monitoring, daemon=True)
    monitoring_thread.start()

    # Run the Flask app with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)


