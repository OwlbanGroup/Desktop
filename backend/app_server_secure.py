#!/usr/bin/env python3
"""
Secure version of the OWLban Flask backend with authentication and authorization
"""

from flask import Flask, send_from_directory, jsonify, request, g
from organizational_leadership import leadership
from revenue_tracking import RevenueTracker
from nvidia_integration import NvidiaIntegration
import os
import subprocess
import requests
from datetime import datetime
from security_config import (
    security_config, user_manager, jwt_manager,
    require_auth, require_rate_limit, add_security_headers,
    validate_input_data, validate_email, validate_username, validate_amount
)

app = Flask(__name__, static_folder='../frontend')

OSCAR_BROOME_URL = os.getenv('OSCAR_BROOME_URL', 'http://localhost:4000')

# Initialize components
revenue_tracker = RevenueTracker()
nvidia_integration = NvidiaIntegration()

# Apply security headers to all responses
@app.after_request
def apply_security_headers(response):
    return add_security_headers(response)

@app.route('/api/auth/login', methods=['POST'])
@require_rate_limit
@validate_input_data(
    required_fields=['username', 'password'],
    field_validators={'username': validate_username}
)
def login():
    """User login endpoint"""
    data = request.get_json()
    username = data['username']
    password = data['password']

    user_data = user_manager.authenticate_user(username, password)
    if not user_data:
        return jsonify({'error': 'Invalid credentials'}), 401

    token = jwt_manager.generate_token(user_data)

    return jsonify({
        'token': token,
        'user': {
            'username': user_data['username'],
            'role': user_data['role'],
            'email': user_data['email']
        }
    })

@app.route('/api/auth/register', methods=['POST'])
@require_rate_limit
@validate_input_data(
    required_fields=['username', 'password', 'email', 'role'],
    field_validators={
        'username': validate_username,
        'email': validate_email
    }
)
def register():
    """User registration endpoint"""
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']
    role = data['role']

    try:
        user_manager.create_user(username, password, role, email)
        return jsonify({'message': 'User created successfully'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/auth/me', methods=['GET'])
@require_auth()
def get_current_user():
    """Get current user information"""
    return jsonify({
        'user': {
            'username': g.user['username'],
            'role': g.user['role'],
            'email': g.user['email']
        }
    })

@app.route('/api/leadership/lead_team', methods=['POST'])
@require_auth(['admin', 'manager'])
@require_rate_limit
@validate_input_data(
    required_fields=['leader_name', 'leadership_style'],
    field_validators={'leadership_style': lambda x: x.upper() in ['DEMOCRATIC', 'AUTHORITATIVE', 'LAISSEZ_FAIRE']}
)
def lead_team():
    data = request.json
    leader_name = data.get('leader_name', 'Alice')
    leadership_style = data.get('leadership_style', 'DEMOCRATIC').upper()
    team_members = data.get('team_members', ['Bob:Developer', 'Charlie:Designer'])

    style = leadership.LeadershipStyle[leadership_style]
    leader = leadership.Leader(leader_name, style)
    leader.set_revenue_tracker(revenue_tracker)
    team = leadership.Team(leader)

    for member_str in team_members:
        if ':' in member_str:
            name, role = member_str.split(':', 1)
        else:
            name, role = member_str, None
        member = leadership.TeamMember(name, role)
        team.add_member(member)

    lead_result = leader.lead_team()
    team_status = team.team_status()

    return jsonify({
        'lead_result': lead_result,
        'team_status': team_status
    })

@app.route('/api/leadership/make_decision', methods=['POST'])
@require_auth(['admin', 'manager'])
@require_rate_limit
@validate_input_data(required_fields=['decision'])
def make_decision():
    data = request.json
    leader_name = data.get('leader_name', 'Alice')
    leadership_style = data.get('leadership_style', 'DEMOCRATIC').upper()
    decision = data.get('decision', 'Implement new project strategy')

    style = leadership.LeadershipStyle[leadership_style]
    leader = leadership.Leader(leader_name, style)
    leader.set_revenue_tracker(revenue_tracker)

    decision_result = leadership.make_decision(leader, decision, revenue_tracker)

    return jsonify({
        'decision_result': decision_result
    })

@app.route('/api/gpu/status', methods=['GET'])
@require_auth()
@require_rate_limit
def gpu_status():
    gpu_settings = nvidia_integration.get_gpu_settings()
    return jsonify(gpu_settings)

@app.route('/api/earnings', methods=['GET'])
@require_auth(['admin', 'manager'])
@require_rate_limit
def earnings_data():
    # Proxy or integrate with OSCAR-BROOME-REVENUE API here
    # For now, serve static files or implement backend logic
    return jsonify({"message": "Earnings data API placeholder"})

# JPMorgan Payment Proxy Routes with enhanced security
@app.route('/api/jpmorgan-payment/create-payment', methods=['POST'])
@require_auth(['admin', 'manager'])
@require_rate_limit
@validate_input_data(
    required_fields=['amount', 'currency'],
    field_validators={
        'amount': validate_amount,
        'currency': lambda x: x.upper() in ['USD', 'EUR', 'GBP']
    }
)
def proxy_create_payment():
    try:
        response = requests.post(
            f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/create-payment",
            json=request.json,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jpmorgan-payment/payment-status/<payment_id>', methods=['GET'])
@require_auth()
@require_rate_limit
def proxy_payment_status(payment_id):
    # Validate payment_id format (basic validation)
    if not payment_id or len(payment_id) > 100:
        return jsonify({'error': 'Invalid payment ID'}), 400

    try:
        response = requests.get(
            f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/payment-status/{payment_id}",
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jpmorgan-payment/refund', methods=['POST'])
@require_auth(['admin'])
@require_rate_limit
@validate_input_data(
    required_fields=['payment_id', 'amount'],
    field_validators={'amount': validate_amount}
)
def proxy_refund():
    try:
        response = requests.post(
            f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/refund",
            json=request.json,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jpmorgan-payment/capture', methods=['POST'])
@require_auth(['admin', 'manager'])
@require_rate_limit
@validate_input_data(
    required_fields=['payment_id', 'amount'],
    field_validators={'amount': validate_amount}
)
def proxy_capture():
    try:
        response = requests.post(
            f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/capture",
            json=request.json,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jpmorgan-payment/void', methods=['POST'])
@require_auth(['admin'])
@require_rate_limit
@validate_input_data(required_fields=['payment_id'])
def proxy_void():
    try:
        response = requests.post(
            f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/void",
            json=request.json,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jpmorgan-payment/transactions', methods=['GET'])
@require_auth(['admin', 'manager'])
@require_rate_limit
def proxy_transactions():
    try:
        params = request.args.to_dict()
        response = requests.get(
            f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/transactions",
            params=params,
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jpmorgan-payment/webhook', methods=['POST'])
@require_rate_limit
def proxy_webhook():
    # Webhook endpoint - no auth required for external service callbacks
    try:
        response = requests.post(
            f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/webhook",
            json=request.json,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jpmorgan-payment/health', methods=['GET'])
@require_auth()
@require_rate_limit
def proxy_health():
    try:
        response = requests.get(f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/health", timeout=30)
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
@require_rate_limit
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'flask': 'running',
            'node_proxy': OSCAR_BROOME_URL
        }
    })

@app.route('/metrics', methods=['GET'])
@require_auth(['admin'])
def metrics():
    """Prometheus metrics endpoint"""
    # In production, integrate with prometheus_client
    return jsonify({
        'app_info': {'version': '1.0.0', 'name': 'owlban'},
        'uptime': (datetime.now() - datetime.min).total_seconds(),
        'active_connections': 1  # Placeholder
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({'error': 'Rate limit exceeded'}), 429

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
