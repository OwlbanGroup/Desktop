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
from nvidia_integration import NvidiaIntegration

app = Flask(__name__, static_folder='./frontend')

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
