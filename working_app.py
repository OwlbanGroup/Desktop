#!/usr/bin/env python3

from flask import Flask, jsonify
import json

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

if __name__ == '__main__':
    print("Starting Flask app...")
    print("Routes available:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule}")
    print("\nApp is ready to run!")
    # app.run(debug=True, host='0.0.0.0', port=5000)
