from flask import Flask, send_from_directory, jsonify, request
import os
import subprocess
import requests
import sys
from datetime import datetime

# Add parent directory to Python path to import modules from root
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

@app.route('/api/financial/forecast', methods=['GET'])
def get_financial_forecast():
    """Get revenue forecasting data"""
    try:
        months_ahead = int(request.args.get('months_ahead', 6))
        method = request.args.get('method', 'linear')
        forecast = advanced_tracker.advanced_forecasting(months_ahead, method)
        return jsonify({
            'success': True,
            'data': forecast
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/financial/alerts', methods=['GET'])
def get_financial_alerts():
    """Get financial alerts and recommendations"""
    try:
        alerts = advanced_tracker.generate_financial_alerts()
        recommendations = advanced_tracker.generate_recommendations(alerts)
        return jsonify({
            'success': True,
            'data': {
                'alerts': alerts,
                'recommendations': recommendations
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/financial/excellence-scorecard', methods=['GET'])
def get_excellence_scorecard():
    """Get financial excellence scorecard"""
    try:
        scorecard = excellence_manager.get_excellence_scorecard()
        return jsonify({
            'success': True,
            'data': scorecard
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/financial/add-record', methods=['POST'])
def add_financial_record():
    """Add a new financial record"""
    try:
        data = request.json
        description = data.get('description')
        amount = data.get('amount')
        category = data.get('category', 'Other')
        source = data.get('source', 'Unknown')
        tags = data.get('tags', [])

        if not description or amount is None:
            return jsonify({
                'success': False,
                'error': 'Description and amount are required'
            }), 400

        category_enum = RevenueCategory(category)
        record = advanced_tracker.add_record(
            description=description,
            amount=float(amount),
            category=category_enum,
            source=source,
            tags=tags
        )

        return jsonify({
            'success': True,
            'data': record.to_dict(),
            'message': 'Financial record added successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/financial/records', methods=['GET'])
def get_financial_records():
    """Get financial records with optional filtering"""
    try:
        category = request.args.get('category')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 100))

        category_filter = RevenueCategory(category) if category else None

        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        records = advanced_tracker.get_all_records(
            category=category_filter,
            start_date=start_date,
            end_date=end_date
        )

        # Limit results
        records = records[:limit]

        return jsonify({
            'success': True,
            'data': [record.to_dict() for record in records],
            'count': len(records)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/financial/kpis', methods=['GET'])
def get_financial_kpis():
    """Get comprehensive financial KPIs"""
    try:
        current_period_days = int(request.args.get('current_period_days', 30))
        previous_period_days = int(request.args.get('previous_period_days', 30))

        kpis = advanced_tracker.calculate_comprehensive_kpis(
            current_period_days=current_period_days,
            previous_period_days=previous_period_days
        )

        return jsonify({
            'success': True,
            'data': kpis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/financial/export', methods=['POST'])
def export_financial_data():
    """Export financial data to file"""
    try:
        data = request.json
        filename = data.get('filename', 'financial_export.json')
        format_type = data.get('format', 'json')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        if format_type == 'json':
            result = advanced_tracker.export_comprehensive_report(
                filename=filename,
                start_date=start_date,
                end_date=end_date
            )
        else:
            result = financial_dashboard.export_dashboard_data(
                filename=filename,
                format=format_type
            )

        return jsonify({
            'success': True,
            'message': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/financial/excellence-report', methods=['POST'])
def generate_excellence_report():
    """Generate comprehensive financial excellence report"""
    try:
        data = request.json
        filename = data.get('filename', 'excellence_report.json')

        result = excellence_manager.generate_excellence_report(filename)

        return jsonify({
            'success': True,
            'message': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# JPMorgan Payment Proxy Routes
@app.route('/api/jpmorgan-payment/create-payment', methods=['POST'])
def proxy_create_payment():
    try:
        response = requests.post(
            f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/create-payment",
            json=request.json,
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jpmorgan-payment/payment-status/<payment_id>', methods=['GET'])
def proxy_payment_status(payment_id):
    try:
        response = requests.get(
            f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/payment-status/{payment_id}"
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jpmorgan-payment/refund', methods=['POST'])
def proxy_refund():
    try:
        response = requests.post(
            f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/refund",
            json=request.json,
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jpmorgan-payment/capture', methods=['POST'])
def proxy_capture():
    try:
        response = requests.post(
            f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/capture",
            json=request.json,
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jpmorgan-payment/void', methods=['POST'])
def proxy_void():
    try:
        response = requests.post(
            f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/void",
            json=request.json,
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jpmorgan-payment/transactions', methods=['GET'])
def proxy_transactions():
    try:
        params = request.args.to_dict()
        response = requests.get(
            f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/transactions",
            params=params
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jpmorgan-payment/webhook', methods=['POST'])
def proxy_webhook():
    try:
        response = requests.post(
            f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/webhook",
            json=request.json,
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jpmorgan-payment/health', methods=['GET'])
def proxy_health():
    try:
        response = requests.get(f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/health")
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

# Login Override Implementation
import uuid
from datetime import datetime, timedelta

# In-memory storage for overrides (in production, use a database)
overrides_db = {}
active_overrides = {}

@app.route('/api/override/emergency', methods=['POST'])
def emergency_override():
    data = request.json
    user_id = data.get('userId')
    reason = data.get('reason', 'emergency_access')
    emergency_code = data.get('emergencyCode')

    if not user_id or not emergency_code:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    if emergency_code != 'OSCAR_BROOME_EMERGENCY_2024':
        return jsonify({'success': False, 'message': 'Invalid emergency code'}), 401

    override_id = str(uuid.uuid4())
    override_data = {
        'id': override_id,
        'userId': user_id,
        'type': 'emergency',
        'reason': reason,
        'createdAt': datetime.now().isoformat(),
        'expiresAt': (datetime.now() + timedelta(hours=24)).isoformat(),
        'status': 'active'
    }

    overrides_db[override_id] = override_data
    active_overrides[user_id] = override_data

    return jsonify({
        'success': True,
        'message': 'Emergency override created successfully',
        'data': {'overrideId': override_id}
    })

@app.route('/api/override/admin', methods=['POST'])
def admin_override():
    data = request.json
    admin_user_id = data.get('adminUserId')
    target_user_id = data.get('targetUserId')
    reason = data.get('reason', 'account_locked')
    justification = data.get('justification')

    if not admin_user_id or not target_user_id or not justification:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    override_id = str(uuid.uuid4())
    override_data = {
        'id': override_id,
        'adminUserId': admin_user_id,
        'targetUserId': target_user_id,
        'type': 'admin',
        'reason': reason,
        'justification': justification,
        'createdAt': datetime.now().isoformat(),
        'expiresAt': (datetime.now() + timedelta(hours=48)).isoformat(),
        'status': 'active'
    }

    overrides_db[override_id] = override_data
    active_overrides[target_user_id] = override_data

    return jsonify({
        'success': True,
        'message': 'Admin override created successfully',
        'data': {'overrideId': override_id}
    })

@app.route('/api/override/technical', methods=['POST'])
def technical_override():
    data = request.json
    support_user_id = data.get('supportUserId')
    target_user_id = data.get('targetUserId')
    reason = data.get('reason', 'technical_issue')
    ticket_number = data.get('ticketNumber')

    if not support_user_id or not target_user_id or not ticket_number:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    override_id = str(uuid.uuid4())
    override_data = {
        'id': override_id,
        'supportUserId': support_user_id,
        'targetUserId': target_user_id,
        'type': 'technical',
        'reason': reason,
        'ticketNumber': ticket_number,
        'createdAt': datetime.now().isoformat(),
        'expiresAt': (datetime.now() + timedelta(hours=12)).isoformat(),
        'status': 'active'
    }

    overrides_db[override_id] = override_data
    active_overrides[target_user_id] = override_data

    return jsonify({
        'success': True,
        'message': 'Technical override created successfully',
        'data': {'overrideId': override_id}
    })

@app.route('/api/override/validate/<override_id>', methods=['POST'])
def validate_override(override_id):
    data = request.json
    user_id = data.get('userId')

    if override_id not in overrides_db:
        return jsonify({'success': False, 'message': 'Override not found'}), 404

    override = overrides_db[override_id]
    if override['status'] != 'active':
        return jsonify({'success': False, 'message': 'Override is not active'}), 400

    if datetime.now() > datetime.fromisoformat(override['expiresAt']):
        override['status'] = 'expired'
        return jsonify({'success': False, 'message': 'Override has expired'}), 400

    return jsonify({
        'success': True,
        'message': 'Override validated successfully',
        'data': override
    })

@app.route('/api/override/revoke/<override_id>', methods=['POST'])
def revoke_override(override_id):
    if override_id not in overrides_db:
        return jsonify({'success': False, 'message': 'Override not found'}), 404

    override = overrides_db[override_id]
    override['status'] = 'revoked'
    override['revokedAt'] = datetime.now().isoformat()

    # Remove from active overrides
    user_id = override.get('userId') or override.get('targetUserId')
    if user_id in active_overrides:
        del active_overrides[user_id]

    return jsonify({
        'success': True,
        'message': 'Override revoked successfully'
    })

@app.route('/api/override/active/<user_id>', methods=['GET'])
def get_active_overrides(user_id):
    if user_id in active_overrides:
        override = active_overrides[user_id]
        if datetime.now() > datetime.fromisoformat(override['expiresAt']):
            override['status'] = 'expired'
            del active_overrides[user_id]
            return jsonify({'success': False, 'message': 'Override has expired'}), 400

        return jsonify({
            'success': True,
            'data': override
        })

    return jsonify({'success': False, 'message': 'No active override found'}), 404

@app.route('/api/override/stats', methods=['GET'])
def get_override_stats():
    total_overrides = len(overrides_db)
    active_count = len([o for o in overrides_db.values() if o['status'] == 'active'])
    expired_count = len([o for o in overrides_db.values() if o['status'] == 'expired'])
    revoked_count = len([o for o in overrides_db.values() if o['status'] == 'revoked'])

    return jsonify({
        'success': True,
        'data': {
            'total': total_overrides,
            'active': active_count,
            'expired': expired_count,
            'revoked': revoked_count
        }
    })

@app.route('/api/override/config', methods=['GET'])
def get_override_config():
    return jsonify({
        'success': True,
        'data': {
            'emergencyCode': 'OSCAR_BROOME_EMERGENCY_2024',
            'maxOverrideDuration': 48,  # hours
            'requireJustification': True,
            'autoExpire': True
        }
    })

@app.route('/api/override/health', methods=['GET'])
def override_health():
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'activeOverrides': len(active_overrides),
        'totalOverrides': len(overrides_db)
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'flask': 'running',
            'node_proxy': OSCAR_BROOME_URL
        }
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    import sys
    import os

    # Change working directory to backend to ensure relative imports and paths work correctly
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Run the Flask app
    app.run(debug=True, port=5000)
