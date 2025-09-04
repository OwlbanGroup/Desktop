#!/usr/bin/env python3

import sys
import os

# Write to file immediately
with open('working_app_output.txt', 'w') as f:
    f.write("Testing working app...\n")

try:
    from flask import Flask, jsonify
    with open('working_app_output.txt', 'a') as f:
        f.write("✅ Flask imported successfully\n")

    app = Flask(__name__)

    @app.route('/')
    def home():
        return jsonify({"message": "Flask app is working!", "status": "success"})

    @app.route('/gpu/status')
    def gpu_status():
        return jsonify({
            "gpu": "NVIDIA RTX 3080",
            "status": "active",
            "temperature": "65°C",
            "memory": "8GB/10GB"
        })

    @app.route('/gpu/settings')
    def gpu_settings():
        return jsonify({
            "resolution": "1920x1080",
            "refresh_rate": "144Hz",
            "color_depth": "32-bit",
            "vsync": "off"
        })

    routes = [str(rule) for rule in app.url_map.iter_rules()]
    gpu_routes = [r for r in routes if 'gpu' in r]

    with open('working_app_output.txt', 'a') as f:
        f.write(f"📊 Total routes: {len(routes)}\n")
        f.write(f"🎮 GPU routes: {len(gpu_routes)}\n")
        f.write("Routes:\n")
        for route in routes:
            f.write(f"  {route}\n")
        f.write("Test completed successfully!\n")

except Exception as e:
    with open('working_app_output.txt', 'a') as f:
        f.write(f"❌ Error: {e}\n")
        import traceback
        f.write(traceback.format_exc() + "\n")

print("Working app test completed. Check working_app_output.txt for results.")
