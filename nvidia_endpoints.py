"""
Additional NVIDIA Control Panel API Endpoints
These endpoints extend the basic GPU status endpoint with comprehensive NVIDIA features
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from flask_limiter import Limiter
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def add_nvidia_endpoints(app, nvidia_interface, limiter, ws_manager):
    """Add all NVIDIA API endpoints to the Flask app"""

    @app.route('/api/gpu/physx', methods=['GET', 'POST'])
    @jwt_required()
    @limiter.limit("20 per minute")
    def gpu_physx():
        """NVIDIA PhysX configuration endpoint"""
        try:
            if request.method == 'GET':
                # Get PhysX configuration
                config = nvidia_interface.get_physx_configuration()
                return jsonify(config)
            else:
                # Set PhysX configuration
                data = request.get_json()
                if not data or 'processor' not in data:
                    return jsonify({'error': 'Missing processor parameter'}), 400

                processor = data['processor']
                if processor not in ['auto', 'cpu', 'gpu']:
                    return jsonify({'error': 'Invalid processor value'}), 400

                result = nvidia_interface.set_physx_configuration(processor)
                return jsonify(result)

        except Exception as e:
            logger.error(f"PhysX configuration error: {e}")
            return jsonify({'error': 'Failed to configure PhysX'}), 500

    @app.route('/api/gpu/performance', methods=['GET'])
    @jwt_required()
    @limiter.limit("30 per minute")
    def gpu_performance():
        """NVIDIA GPU performance monitoring endpoint"""
        try:
            # Get performance counters
            performance_data = nvidia_interface.get_performance_counters()
            return jsonify(performance_data)

        except Exception as e:
            logger.error(f"Performance monitoring error: {e}")
            return jsonify({'error': 'Failed to get performance data'}), 500

    @app.route('/api/gpu/frame-sync', methods=['GET', 'POST'])
    @jwt_required()
    @limiter.limit("20 per minute")
    def gpu_frame_sync():
        """NVIDIA frame sync configuration endpoint"""
        try:
            if request.method == 'GET':
                # Get frame sync mode
                mode = nvidia_interface.get_frame_sync_mode()
                return jsonify(mode)
            else:
                # Set frame sync mode
                data = request.get_json()
                if not data or 'mode' not in data:
                    return jsonify({'error': 'Missing mode parameter'}), 400

                mode = data['mode']
                if mode not in ['disabled', 'swap_group', 'swap_barrier']:
                    return jsonify({'error': 'Invalid frame sync mode'}), 400

                result = nvidia_interface.set_frame_sync_mode(mode)
                return jsonify(result)

        except Exception as e:
            logger.error(f"Frame sync configuration error: {e}")
            return jsonify({'error': 'Failed to configure frame sync'}), 500

    @app.route('/api/gpu/sdi-output', methods=['GET', 'POST'])
    @jwt_required()
    @limiter.limit("20 per minute")
    def gpu_sdi_output():
        """NVIDIA SDI output configuration endpoint"""
        try:
            if request.method == 'GET':
                # Get SDI output configuration
                config = nvidia_interface.get_sdi_output_config()
                return jsonify(config)
            else:
                # Set SDI output configuration
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'Missing configuration data'}), 400

                result = nvidia_interface.set_sdi_output_config(data)
                return jsonify(result)

        except Exception as e:
            logger.error(f"SDI output configuration error: {e}")
            return jsonify({'error': 'Failed to configure SDI output'}), 500

    @app.route('/api/gpu/edid', methods=['GET', 'POST'])
    @jwt_required()
    @limiter.limit("20 per minute")
    def gpu_edid():
        """NVIDIA EDID management endpoint"""
        try:
            if request.method == 'GET':
                # Get EDID information
                edid_info = nvidia_interface.get_edid_info()
                return jsonify(edid_info)
            else:
                # Apply or reset EDID
                data = request.get_json()
                if not data or 'action' not in data:
                    return jsonify({'error': 'Missing action parameter'}), 400

                action = data['action']
                if action == 'apply':
                    if 'edid_data' not in data:
                        return jsonify({'error': 'Missing edid_data parameter'}), 400
                    result = nvidia_interface.apply_edid(data['edid_data'])
                elif action == 'reset':
                    result = nvidia_interface.reset_edid()
                else:
                    return jsonify({'error': 'Invalid action'}), 400

                return jsonify(result)

        except Exception as e:
            logger.error(f"EDID management error: {e}")
            return jsonify({'error': 'Failed to manage EDID'}), 500

    @app.route('/api/gpu/workstation', methods=['GET', 'POST'])
    @jwt_required()
    @limiter.limit("20 per minute")
    def gpu_workstation():
        """NVIDIA workstation features endpoint"""
        try:
            if request.method == 'GET':
                # Get workstation features
                features = nvidia_interface.get_workstation_features()
                return jsonify(features)
            else:
                # Set workstation feature
                data = request.get_json()
                if not data or 'feature' not in data or 'enabled' not in data:
                    return jsonify({'error': 'Missing feature or enabled parameters'}), 400

                feature = data['feature']
                enabled = data['enabled']

                result = nvidia_interface.set_workstation_feature(feature, enabled)
                return jsonify(result)

        except Exception as e:
            logger.error(f"Workstation features error: {e}")
            return jsonify({'error': 'Failed to manage workstation features'}), 500

    @app.route('/api/gpu/profiles', methods=['GET', 'POST'])
    @jwt_required()
    @limiter.limit("15 per minute")
    def gpu_profiles():
        """NVIDIA GPU profiles management endpoint"""
        try:
            if request.method == 'GET':
                # Get GPU profiles
                profiles = nvidia_interface.get_gpu_profiles()
                return jsonify(profiles)
            else:
                # Create, apply, or delete profile
                data = request.get_json()
                if not data or 'action' not in data:
                    return jsonify({'error': 'Missing action parameter'}), 400

                action = data['action']
                if action == 'create':
                    if 'profile_name' not in data:
                        return jsonify({'error': 'Missing profile_name parameter'}), 400
                    result = nvidia_interface.create_gpu_profile(data['profile_name'], data.get('settings', {}))
                elif action == 'apply':
                    if 'profile_name' not in data:
                        return jsonify({'error': 'Missing profile_name parameter'}), 400
                    result = nvidia_interface.apply_gpu_profile(data['profile_name'])
                elif action == 'delete':
                    if 'profile_name' not in data:
                        return jsonify({'error': 'Missing profile_name parameter'}), 400
                    result = nvidia_interface.delete_gpu_profile(data['profile_name'])
                else:
                    return jsonify({'error': 'Invalid action'}), 400

                return jsonify(result)

        except Exception as e:
            logger.error(f"GPU profiles management error: {e}")
            return jsonify({'error': 'Failed to manage GPU profiles'}), 500

    @app.route('/api/gpu/clone-displays', methods=['POST'])
    @jwt_required()
    @limiter.limit("10 per minute")
    def gpu_clone_displays():
        """NVIDIA display cloning endpoint"""
        try:
            data = request.get_json()
            if not data or 'source_display' not in data or 'target_displays' not in data:
                return jsonify({'error': 'Missing source_display or target_displays parameters'}), 400

            source_display = data['source_display']
            target_displays = data['target_displays']

            if not isinstance(target_displays, list) or len(target_displays) == 0:
                return jsonify({'error': 'target_displays must be a non-empty list'}), 400

            result = nvidia_interface.clone_displays(source_display, target_displays)
            return jsonify(result)

        except Exception as e:
            logger.error(f"Display cloning error: {e}")
            return jsonify({'error': 'Failed to clone displays'}), 500

    logger.info("✅ NVIDIA Control Panel endpoints added successfully")
    return app
