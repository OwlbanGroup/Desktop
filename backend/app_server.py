from flask import Flask, send_from_directory, jsonify, request
from organizational_leadership import leadership
from revenue_tracking import RevenueTracker
from nvidia_integration import NvidiaIntegration
import os
import subprocess
import requests
from datetime import datetime

app = Flask(__name__, static_folder='../frontend')

OSCAR_BROOME_URL = os.getenv('OSCAR_BROOME_URL', 'http://localhost:4000')

# Initialize components
revenue_tracker = RevenueTracker()
nvidia_integration = NvidiaIntegration()

@app.route('/api/leadership/lead_team', methods=['POST'])
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
def gpu_status():
    gpu_settings = nvidia_integration.get_gpu_settings()
    return jsonify(gpu_settings)

@app.route('/api/earnings', methods=['GET'])
def earnings_data():
    # Proxy or integrate with OSCAR-BROOME-REVENUE API here
    # For now, serve static files or implement backend logic
    return jsonify({"message": "Earnings data API placeholder"})

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

# Login Override Proxy Routes
@app.route('/api/override/emergency', methods=['POST'])
def proxy_emergency_override():
    try:
        response = requests.post(
            f"{OSCAR_BROOME_URL}/api/override/emergency",
            json=request.json,
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/override/admin', methods=['POST'])
def proxy_admin_override():
    try:
        response = requests.post(
            f"{OSCAR_BROOME_URL}/api/override/admin",
            json=request.json,
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/override/technical', methods=['POST'])
def proxy_technical_override():
    try:
        response = requests.post(
            f"{OSCAR_BROOME_URL}/api/override/technical",
            json=request.json,
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/override/validate/<override_id>', methods=['POST'])
def proxy_validate_override(override_id):
    try:
        response = requests.post(
            f"{OSCAR_BROOME_URL}/api/override/validate/{override_id}",
            json=request.json,
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/override/revoke/<override_id>', methods=['POST'])
def proxy_revoke_override(override_id):
    try:
        response = requests.post(
            f"{OSCAR_BROOME_URL}/api/override/revoke/{override_id}",
            json=request.json,
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/override/active/<user_id>', methods=['GET'])
def proxy_active_overrides(user_id):
    try:
        response = requests.get(f"{OSCAR_BROOME_URL}/api/override/active/{user_id}")
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/override/stats', methods=['GET'])
def proxy_override_stats():
    try:
        response = requests.get(f"{OSCAR_BROOME_URL}/api/override/stats")
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/override/config', methods=['GET'])
def proxy_override_config():
    try:
        response = requests.get(f"{OSCAR_BROOME_URL}/api/override/config")
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/override/health', methods=['GET'])
def proxy_override_health():
    try:
        response = requests.get(f"{OSCAR_BROOME_URL}/api/override/health")
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

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
