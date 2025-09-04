#!/usr/bin/env python3
"""
Integrated Financial Services Application with NVIDIA AI Integration

This application combines:
- Organizational Leadership Management
- Revenue Tracking
- NVIDIA GPU Integration (Fixed)
- Financial Services (Chase Auto/Mortgage)
- JPMorgan Payment Processing
- Login Override System
- Comprehensive API Endpoints

Features:
- GPU-accelerated financial processing
- NVIDIA Control Panel integration
- Employee benefits management
- Auto loan and mortgage processing
- Payment gateway integration
- Emergency access controls
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys
import json
import uuid
from datetime import datetime, timedelta
import importlib.util
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add OSCAR-BROOME-REVENUE directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'OSCAR-BROOME-REVENUE'))

# Import core modules
from organizational_leadership import leadership
from revenue_tracking import RevenueTracker
from nvidia_integration_fixed import NvidiaIntegration

# Import financial modules using importlib
try:
    spec_chase_mortgage = importlib.util.spec_from_file_location(
        "chase_mortgage",
        os.path.join(os.getcwd(), 'OSCAR-BROOME-REVENUE', 'earnings_dashboard', 'chase_mortgage.py')
    )
    chase_mortgage = importlib.util.module_from_spec(spec_chase_mortgage)
    spec_chase_mortgage.loader.exec_module(chase_mortgage)

    spec_chase_auto = importlib.util.spec_from_file_location(
        "chase_auto_finance",
        os.path.join(os.getcwd(), 'OSCAR-BROOME-REVENUE', 'earnings_dashboard', 'chase_auto_finance.py')
    )
    chase_auto_finance = importlib.util.module_from_spec(spec_chase_auto)
    spec_chase_auto.loader.exec_module(chase_auto_finance)

    logger.info("Financial modules loaded successfully")
except Exception as e:
    logger.warning(f"Some financial modules could not be loaded: {e}")

# Initialize Flask app
app = Flask(__name__, static_folder='./frontend')
CORS(app)

# Initialize core components
revenue_tracker = RevenueTracker()
nvidia_integration = NvidiaIntegration()

# In-memory storage for overrides
overrides_db = {}
active_overrides = {}

# OSCAR-BROOME URL for proxying
OSCAR_BROOME_URL = os.getenv('OSCAR_BROOME_URL', 'http://localhost:4000')

# =============================================================================
# NVIDIA INTEGRATION ENDPOINTS
# =============================================================================

@app.route('/api/nvidia/gpu/status', methods=['GET'])
def get_gpu_status():
    """Get comprehensive GPU status and settings."""
    try:
        gpu_settings = nvidia_integration.get_gpu_settings()
        return jsonify({
            'success': True,
            'data': gpu_settings,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/nvidia/gpu/settings', methods=['POST'])
def update_gpu_settings():
    """Update GPU settings."""
    try:
        settings = request.json
        result = nvidia_integration.set_gpu_settings(settings)
        return jsonify({
            'success': True,
            'message': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/nvidia/benefits', methods=['GET'])
def get_nvidia_benefits():
    """Get NVIDIA employee benefits and resources."""
    try:
        benefits = nvidia_integration.get_benefits_resources()
        return jsonify({
            'success': True,
            'data': benefits,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/nvidia/health-providers', methods=['GET'])
def get_health_providers():
    """Get health provider network information."""
    try:
        providers = nvidia_integration.get_health_provider_network()
        return jsonify({
            'success': True,
            'data': providers,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/nvidia/contacts', methods=['GET'])
def get_nvidia_contacts():
    """Get NVIDIA contacts and policy information."""
    try:
        contacts = nvidia_integration.get_contacts_and_policy_numbers()
        return jsonify({
            'success': True,
            'data': contacts,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/nvidia/drivers', methods=['GET'])
def get_driver_updates():
    """Get NVIDIA driver updates and versions."""
    try:
        drivers = nvidia_integration.get_driver_updates()
        return jsonify({
            'success': True,
            'data': drivers,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/nvidia/auto-loan', methods=['POST'])
def apply_auto_loan():
    """Apply for NVIDIA auto loan."""
    try:
        data = request.json
        vehicle_info = data.get('vehicle_info', {})
        applicant_info = data.get('applicant_info', {})

        result = nvidia_integration.apply_for_auto_loan(vehicle_info, applicant_info)
        return jsonify({
            'success': result.get('success', False),
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/nvidia/loan-status/<application_id>', methods=['GET'])
def get_loan_status(application_id):
    """Check loan application status."""
    try:
        status = nvidia_integration.get_loan_status(application_id)
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/nvidia/purchase-integration', methods=['POST'])
def integrate_auto_purchase():
    """Integrate auto purchase with financing."""
    try:
        data = request.json
        vehicle_info = data.get('vehicle_info', {})
        applicant_info = data.get('applicant_info', {})

        result = nvidia_integration.integrate_auto_purchase_with_loan(vehicle_info, applicant_info)
        return jsonify({
            'success': result.get('success', False),
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# =============================================================================
# ORGANIZATIONAL LEADERSHIP ENDPOINTS
# =============================================================================

@app.route('/api/leadership/team', methods=['POST'])
def create_team():
    """Create and manage organizational team."""
    try:
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
            try:
                member = leadership.TeamMember(name, role)
                team.add_member(member)
            except ValueError as e:
                logger.warning(f"Error adding team member: {e}")

        return jsonify({
            'success': True,
            'data': {
                'leader': leader_name,
                'style': leadership_style,
                'team_size': len(team.members),
                'lead_result': leader.lead_team(),
                'team_status': team.team_status()
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/leadership/decision', methods=['POST'])
def make_leadership_decision():
    """Make leadership decision with revenue tracking."""
    try:
        data = request.json
        leader_name = data.get('leader_name', 'Alice')
        leadership_style = data.get('leadership_style', 'DEMOCRATIC').upper()
        decision = data.get('decision', 'Implement new project strategy')

        style = leadership.LeadershipStyle[leadership_style]
        leader = leadership.Leader(leader_name, style)
        leader.set_revenue_tracker(revenue_tracker)

        decision_result = leadership.make_decision(leader, decision, revenue_tracker)

        return jsonify({
            'success': True,
            'data': {
                'decision': decision,
                'result': decision_result
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# =============================================================================
# FINANCIAL SERVICES ENDPOINTS
# =============================================================================

@app.route('/api/finance/mortgage', methods=['POST'])
def process_mortgage():
    """Process mortgage application."""
    try:
        data = request.json
        # This would integrate with Chase mortgage processing
        return jsonify({
            'success': True,
            'message': 'Mortgage application received',
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/finance/auto-finance', methods=['POST'])
def process_auto_finance():
    """Process auto finance application."""
    try:
        data = request.json
        # This would integrate with Chase auto finance processing
        return jsonify({
            'success': True,
            'message': 'Auto finance application received',
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# =============================================================================
# JPMORGAN PAYMENT ENDPOINTS (Proxy)
# =============================================================================

@app.route('/api/payment/create', methods=['POST'])
def create_payment():
    """Create payment through JPMorgan."""
    try:
        import requests
        response = requests.post(
            f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/create-payment",
            json=request.json,
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/payment/status/<payment_id>', methods=['GET'])
def payment_status(payment_id):
    """Check payment status."""
    try:
        import requests
        response = requests.get(
            f"{OSCAR_BROOME_URL}/api/jpmorgan-payment/payment-status/{payment_id}"
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# =============================================================================
# LOGIN OVERRIDE SYSTEM
# =============================================================================

@app.route('/api/override/emergency', methods=['POST'])
def emergency_override():
    """Create emergency override."""
    try:
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
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/override/admin', methods=['POST'])
def admin_override():
    """Create admin override."""
    try:
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
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/override/active/<user_id>', methods=['GET'])
def get_active_override(user_id):
    """Get active override for user."""
    try:
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
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# =============================================================================
# SYSTEM HEALTH AND MONITORING
# =============================================================================

@app.route('/api/health', methods=['GET'])
def system_health():
    """Get comprehensive system health status."""
    try:
        gpu_status = nvidia_integration.get_gpu_settings()

        return jsonify({
            'success': True,
            'data': {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'services': {
                    'flask': 'running',
                    'nvidia_integration': 'active',
                    'gpu_status': 'available' if gpu_status else 'unavailable',
                    'leadership_system': 'active',
                    'revenue_tracking': 'active',
                    'payment_gateway': 'proxy_active',
                    'override_system': 'active'
                },
                'active_overrides': len(active_overrides),
                'total_overrides': len(overrides_db)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/system/info', methods=['GET'])
def system_info():
    """Get comprehensive system information."""
    try:
        gpu_info = nvidia_integration.get_gpu_settings()

        return jsonify({
            'success': True,
            'data': {
                'system': {
                    'name': 'Integrated Financial Services Platform',
                    'version': '2.0.0',
                    'nvidia_integration': 'enabled',
                    'modules': [
                        'organizational_leadership',
                        'revenue_tracking',
                        'nvidia_integration_fixed',
                        'financial_services',
                        'payment_processing',
                        'login_override_system'
                    ]
                },
                'gpu': gpu_info,
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# =============================================================================
# FRONTEND SERVING
# =============================================================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve frontend files."""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index_enhanced.html')

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application entry point."""
    print("=" * 80)
    print("INTEGRATED FINANCIAL SERVICES APPLICATION WITH NVIDIA AI")
    print("=" * 80)
    print("Features:")
    print("✓ NVIDIA GPU Integration (Fixed)")
    print("✓ Organizational Leadership Management")
    print("✓ Revenue Tracking System")
    print("✓ Financial Services (Chase Auto/Mortgage)")
    print("✓ JPMorgan Payment Processing")
    print("✓ Login Override System")
    print("✓ Comprehensive API Endpoints")
    print("=" * 80)

    # Test NVIDIA integration on startup
    try:
        gpu_status = nvidia_integration.get_gpu_settings()
        print(f"✓ NVIDIA Integration: Active (GPU settings retrieved)")
    except Exception as e:
        print(f"⚠ NVIDIA Integration: Limited functionality ({e})")

    print("\n🚀 Starting Flask application...")
    print("📍 Local: http://localhost:5000")
    print("🌐 Network: http://0.0.0.0:5000")

    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )

if __name__ == '__main__':
    main()
