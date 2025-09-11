"""
Merger Analytics API Endpoints
Provides REST API endpoints for merger analytics functionality
"""

from flask import Blueprint, jsonify, request
import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from merger_integration import merger_integration

# Create blueprint for merger endpoints
merger_bp = Blueprint('merger', __name__, url_prefix='/api/merger')

@merger_bp.route('/overview', methods=['GET'])
def get_merger_overview():
    """Get comprehensive merger overview"""
    result = merger_integration.get_merger_overview()
    return jsonify(result), 200 if result['success'] else 500

@merger_bp.route('/pre-merger-analysis', methods=['GET'])
def get_pre_merger_analysis():
    """Get pre-merger financial analysis"""
    result = merger_integration.get_pre_merger_analysis()
    return jsonify(result), 200 if result['success'] else 500

@merger_bp.route('/synergy-analysis', methods=['GET'])
def get_synergy_analysis():
    """Get synergy analysis and projections"""
    result = merger_integration.get_synergy_analysis()
    return jsonify(result), 200 if result['success'] else 500

@merger_bp.route('/integration-costs', methods=['GET'])
def get_integration_costs():
    """Get integration cost projections"""
    result = merger_integration.get_integration_costs()
    return jsonify(result), 200 if result['success'] else 500

@merger_bp.route('/value-timeline', methods=['GET'])
def get_value_realization_timeline():
    """Get value realization timeline"""
    result = merger_integration.get_value_realization_timeline()
    return jsonify(result), 200 if result['success'] else 500

@merger_bp.route('/risk-assessment', methods=['GET'])
def get_risk_assessment():
    """Get comprehensive risk assessment"""
    result = merger_integration.get_risk_assessment()
    return jsonify(result), 200 if result['success'] else 500

@merger_bp.route('/post-merger-performance', methods=['GET'])
def get_post_merger_performance():
    """Get post-merger performance analysis"""
    result = merger_integration.get_post_merger_performance()
    return jsonify(result), 200 if result['success'] else 500

@merger_bp.route('/dashboard-data', methods=['GET'])
def get_merger_dashboard_data():
    """Get data for merger dashboard visualization"""
    result = merger_integration.get_merger_dashboard_data()
    return jsonify(result), 200 if result['success'] else 500

@merger_bp.route('/executive-report', methods=['POST'])
def generate_executive_report():
    """Generate executive merger report"""
    data = request.json or {}
    filename = data.get('filename')

    result = merger_integration.generate_executive_report(filename)
    return jsonify(result), 200 if result['success'] else 500

@merger_bp.route('/health', methods=['GET'])
def merger_health_check():
    """Health check for merger analytics service"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'merger_analytics',
        'version': '1.0.0'
    })

# Function to register the blueprint with the main app
def register_merger_endpoints(app):
    """Register merger endpoints with the Flask application"""
    app.register_blueprint(merger_bp)
    print("Merger analytics endpoints registered successfully")
