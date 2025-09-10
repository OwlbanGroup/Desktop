#!/usr/bin/env python3
"""
Simple Flask app for testing basic functionality
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return {"message": "Flask app is working!", "status": "success"}

@app.route('/chase-credit-cards')
def chase_credit_cards():
    return {"message": "Chase Credit Cards endpoint working", "status": "success"}

@app.route('/chase-mortgage')
def chase_mortgage():
    return {"message": "Chase Mortgage endpoint working", "status": "success"}

@app.route('/chase-auto-finance')
def chase_auto_finance():
    return {"message": "Chase Auto Finance endpoint working", "status": "success"}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
