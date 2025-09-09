"""
Financial Excellence Dashboard

A comprehensive web-based dashboard for financial analytics and reporting,
featuring real-time metrics, AI-powered insights, and executive-level reporting.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Flask, render_template_string, request, jsonify
from financial_analytics_engine import AdvancedRevenueTracker, RevenueCategory
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

class FinancialExcellenceDashboard:
    """Modern financial dashboard with real-time analytics and AI insights"""

    def __init__(self, tracker: AdvancedRevenueTracker):
        self.tracker = tracker
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        """Set up Flask routes for the dashboard"""

        @self.app.route('/')
        def dashboard():
            return render_template_string(self.get_dashboard_html())

        @self.app.route('/api/dashboard-data')
        def dashboard_data():
            period_days = int(request.args.get('period', 30))
            data = self.tracker.generate_executive_dashboard(period_days)
            return jsonify(data)

        @self.app.route('/api/alerts')
        def alerts():
            alerts = self.tracker.generate_financial_alerts()
            return jsonify({'alerts': alerts})

        @self.app.route('/api/forecast')
        def forecast():
            days_ahead = int(request.args.get('days', 30))
            forecast = self.tracker.ai_powered_forecasting(days_ahead)
            return jsonify(forecast)

        @self.app.route('/api/risk-analysis')
        def risk_analysis():
            risk = self.tracker.ai_risk_analysis()
            return jsonify(risk)

        @self.app.route('/api/export-report')
        def export_report():
            filename = f"financial_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join('reports', filename)
            os.makedirs('reports', exist_ok=True)

            result = self.tracker.export_comprehensive_report(filepath)
            return jsonify({'message': result, 'filename': filename})

    def get_dashboard_html(self) -> str:
        """Generate the main dashboard HTML template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Excellence Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .metric-card { transition: all 0.3s ease; }
        .metric-card:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
        .alert-critical { animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
        .chart-container { min-height: 400px; }
    </style>
</head>
<body class="bg-gray-50">
    <div id="app" class="min-h-screen">
        <!-- Header -->
        <header class="bg-white shadow-lg">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between items-center py-6">
                    <div class="flex items-center">
                        <i class="fas fa-chart-line text-3xl text-blue-600 mr-3"></i>
                        <div>
                            <h1 class="text-3xl font-bold text-gray-900">Financial Excellence Dashboard</h1>
                            <p class="text-gray-600">AI-Powered Financial Analytics & Insights</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-4">
                        <select id="period-select" class="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                            <option value="7">Last 7 days</option>
                            <option value="30" selected>Last 30 days</option>
                            <option value="90">Last 90 days</option>
                            <option value="365">Last year</option>
                        </select>
                        <button id="export-btn" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center">
                            <i class="fas fa-download mr-2"></i>Export Report
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <!-- Loading State -->
            <div id="loading" class="flex justify-center items-center py-20">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <span class="ml-3 text-gray-600">Loading dashboard data...</span>
            </div>

            <!-- Dashboard Content -->
            <div id="dashboard-content" class="hidden">
                <!-- Alerts Section -->
                <div id="alerts-section" class="mb-8">
                    <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                        <i class="fas fa-exclamation-triangle text-yellow-500 mr-2"></i>
                        Active Alerts
                    </h2>
                    <div id="alerts-container" class="space-y-3"></div>
                </div>

                <!-- Key Metrics -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <div class="metric-card bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <i class="fas fa-dollar-sign text-2xl text-green-600"></i>
                            </div>
                            <div class="ml-4">
                                <dt class="text-sm font-medium text-gray-500 truncate">Total Revenue</dt>
                                <dd id="total-revenue" class="text-2xl font-semibold text-gray-900">$0.00</dd>
                            </div>
                        </div>
                    </div>

                    <div class="metric-card bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <i class="fas fa-chart-line text-2xl text-blue-600"></i>
                            </div>
                            <div class="ml-4">
                                <dt class="text-sm font-medium text-gray-500 truncate">Growth Rate</dt>
                                <dd id="growth-rate" class="text-2xl font-semibold text-gray-900">0.0%</dd>
                            </div>
                        </div>
                    </div>

                    <div class="metric-card bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <i class="fas fa-shopping-cart text-2xl text-purple-600"></i>
                            </div>
                            <div class="ml-4">
                                <dt class="text-sm font-medium text-gray-500 truncate">Transactions</dt>
                                <dd id="total-transactions" class="text-2xl font-semibold text-gray-900">0</dd>
                            </div>
                        </div>
                    </div>

                    <div class="metric-card bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <i class="fas fa-brain text-2xl text-indigo-600"></i>
                            </div>
                            <div class="ml-4">
                                <dt class="text-sm font-medium text-gray-500 truncate">AI Risk Level</dt>
                                <dd id="ai-risk-level" class="text-2xl font-semibold text-gray-900">Low</dd>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Charts Grid -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                    <!-- Revenue Trend Chart -->
                    <div class="bg-white rounded-lg shadow p-6">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">Revenue Trend</h3>
                        <div id="revenue-trend-chart" class="chart-container"></div>
                    </div>

                    <!-- Category Breakdown Chart -->
                    <div class="bg-white rounded-lg shadow p-6">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">Revenue by Category</h3>
                        <div id="category-breakdown-chart" class="chart-container"></div>
                    </div>
                </div>

                <!-- AI Insights Section -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                    <!-- AI Forecast -->
                    <div class="bg-white rounded-lg shadow p-6">
                        <h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
                            <i class="fas fa-robot text-blue-600 mr-2"></i>
                            AI Revenue Forecast
                        </h3>
                        <div id="ai-forecast-content" class="space-y-4">
                            <div class="text-center py-8">
                                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                                <p class="mt-2 text-gray-600">Generating AI forecast...</p>
                            </div>
                        </div>
                    </div>

                    <!-- Risk Analysis -->
                    <div class="bg-white rounded-lg shadow p-6">
                        <h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
                            <i class="fas fa-shield-alt text-red-600 mr-2"></i>
                            Risk Analysis
                        </h3>
                        <div id="risk-analysis-content" class="space-y-4">
                            <div class="text-center py-8">
                                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600 mx-auto"></div>
                                <p class="mt-2 text-gray-600">Analyzing financial risks...</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Recommendations Section -->
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
                        <i class="fas fa-lightbulb text-yellow-600 mr-2"></i>
                        AI Recommendations
                    </h3>
                    <div id="recommendations-content" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="text-center py-8 col-span-2">
                            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-600 mx-auto"></div>
                            <p class="mt-2 text-gray-600">Generating recommendations...</p>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        let dashboardData = {};
        let alertsData = [];
        let forecastData = {};
        let riskData = {};

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboardData();
            setupEventListeners();
        });

        function setupEventListeners() {
            // Period selector
            document.getElementById('period-select').addEventListener('change', function() {
                loadDashboardData();
            });

            // Export button
            document.getElementById('export-btn').addEventListener('click', function() {
                exportReport();
            });
        }

        async function loadDashboardData() {
            const period = document.getElementById('period-select').value;
            showLoading();

            try {
                // Load all data in parallel
                const [dashboardResponse, alertsResponse, forecastResponse, riskResponse] = await Promise.all([
                    fetch(`/api/dashboard-data?period=${period}`),
                    fetch('/api/alerts'),
                    fetch(`/api/forecast?days=${period}`),
                    fetch('/api/risk-analysis')
                ]);

                dashboardData = await dashboardResponse.json();
                alertsData = await alertsResponse.json().then(data => data.alerts);
                forecastData = await forecastResponse.json();
                riskData = await riskResponse.json();

                updateDashboard();
                hideLoading();

            } catch (error) {
                console.error('Error loading dashboard data:', error);
                hideLoading();
                showError('Failed to load dashboard data');
            }
        }

        function updateDashboard() {
            updateMetrics();
            updateAlerts();
            updateCharts();
            updateAIInsights();
            updateRecommendations();
        }

        function updateMetrics() {
            const metrics = dashboardData.summary_metrics || {};
            const kpis = dashboardData.kpis || {};

            document.getElementById('total-revenue').textContent = formatCurrency(metrics.total_revenue || 0);
            document.getElementById('growth-rate').textContent = `${(kpis.growth_rate || 0).toFixed(1)}%`;
            document.getElementById('total-transactions').textContent = metrics.total_transactions || 0;

            const riskLevel = riskData.risk_level || 'Low';
            const riskElement = document.getElementById('ai-risk-level');
            riskElement.textContent = riskLevel;
            riskElement.className = `text-2xl font-semibold ${getRiskColor(riskLevel)}`;
        }

        function updateAlerts() {
            const container = document.getElementById('alerts-container');
            const section = document.getElementById('alerts-section');

            if (alertsData.length === 0) {
                section.style.display = 'none';
                return;
            }

            section.style.display = 'block';
            container.innerHTML = '';

            alertsData.forEach(alert => {
                const alertDiv = document.createElement('div');
                alertDiv.className = `p-4 rounded-md border-l-4 ${getAlertStyle(alert.type)} ${alert.type === 'critical' ? 'alert-critical' : ''}`;

                alertDiv.innerHTML = `
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <i class="fas ${getAlertIcon(alert.type)}"></i>
                        </div>
                        <div class="ml-3 flex-1">
                            <p class="text-sm font-medium text-gray-800">${alert.message}</p>
                            <p class="text-sm text-gray-600 mt-1">${alert.recommendation}</p>
                        </div>
                        <div class="ml-auto pl-3">
                            <div class="flex items-center">
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityStyle(alert.severity)}">
                                    ${alert.severity.toUpperCase()}
                                </span>
                            </div>
                        </div>
                    </div>
                `;

                container.appendChild(alertDiv);
            });
        }

        function updateCharts() {
            updateRevenueTrendChart();
            updateCategoryBreakdownChart();
        }

        function updateRevenueTrendChart() {
            const trends = dashboardData.trends || {};
            const monthlyData = trends.monthly_revenue || [];

            if (monthlyData.length === 0) return;

            const months = monthlyData.map(item => item.month);
            const revenues = monthlyData.map(item => item.total);

            const trace = {
                x: months,
                y: revenues,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Revenue',
                line: {color: '#3B82F6', width: 3},
                marker: {color: '#1D4ED8', size: 8}
            };

            const layout = {
                margin: {l: 40, r: 40, t: 20, b: 40},
                xaxis: {title: 'Month'},
                yaxis: {title: 'Revenue ($)', tickformat: ',.0f'},
                showlegend: false
            };

            Plotly.newPlot('revenue-trend-chart', [trace], layout, {responsive: true});
        }

        function updateCategoryBreakdownChart() {
            const categoryData = dashboardData.category_performance || {};
            const breakdown = categoryData.breakdown || {};

            if (Object.keys(breakdown).length === 0) return;

            const categories = Object.keys(breakdown);
            const values = Object.values(breakdown);

            const data = [{
                labels: categories,
                values: values,
                type: 'pie',
                textinfo: 'label+percent',
                textposition: 'outside',
                marker: {
                    colors: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4']
                }
            }];

            const layout = {
                margin: {l: 20, r: 20, t: 20, b: 20},
                showlegend: true,
                legend: {orientation: 'h', y: -0.2}
            };

            Plotly.newPlot('category-breakdown-chart', data, layout, {responsive: true});
        }

        function updateAIInsights() {
            updateAIForecast();
            updateRiskAnalysis();
        }

        function updateAIForecast() {
            const container = document.getElementById('ai-forecast-content');

            if (forecastData.error) {
                container.innerHTML = `
                    <div class="text-center py-8">
                        <i class="fas fa-exclamation-triangle text-yellow-500 text-3xl mb-2"></i>
                        <p class="text-gray-600">${forecastData.error}</p>
                    </div>
                `;
                return;
            }

            const forecast = forecastData.ai_forecast || {};
            if (!forecast.predicted_revenue) {
                container.innerHTML = `
                    <div class="text-center py-8">
                        <i class="fas fa-chart-line text-gray-400 text-3xl mb-2"></i>
                        <p class="text-gray-600">Insufficient data for AI forecasting</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = `
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-blue-50 p-4 rounded-lg">
                        <div class="text-sm text-blue-600 font-medium">Predicted Revenue</div>
                        <div class="text-2xl font-bold text-blue-800">${formatCurrency(forecast.predicted_revenue)}</div>
                    </div>
                    <div class="bg-green-50 p-4 rounded-lg">
                        <div class="text-sm text-green-600 font-medium">Confidence Range</div>
                        <div class="text-lg font-semibold text-green-800">
                            ${formatCurrency(forecast.confidence_lower)} - ${formatCurrency(forecast.confidence_upper)}
                        </div>
                    </div>
                </div>
                <div class="mt-4">
                    <div class="text-sm text-gray-600">
                        <i class="fas fa-calendar-alt mr-1"></i>
                        Prediction for: ${new Date(forecast.prediction_date).toLocaleDateString()}
                    </div>
                    <div class="text-sm text-gray-600 mt-1">
                        <i class="fas fa-brain mr-1"></i>
                        Model Accuracy: ${forecast.model_accuracy || 'Medium'}
                    </div>
                </div>
            `;
        }

        function updateRiskAnalysis() {
            const container = document.getElementById('risk-analysis-content');

            if (riskData.error) {
                container.innerHTML = `
                    <div class="text-center py-8">
                        <i class="fas fa-exclamation-triangle text-yellow-500 text-3xl mb-2"></i>
                        <p class="text-gray-600">${riskData.error}</p>
                    </div>
                `;
                return;
            }

            const riskFactors = riskData.risk_factors || [];
            const recommendations = riskData.recommendations || [];

            container.innerHTML = `
                <div class="mb-4">
                    <div class="flex items-center justify-between">
                        <span class="text-sm font-medium text-gray-700">Risk Level</span>
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskBadgeColor(riskData.risk_level)}">
                            ${riskData.risk_level}
                        </span>
                    </div>
                    <div class="mt-2">
                        <div class="text-2xl font-bold ${getRiskColor(riskData.risk_level)}">${riskData.risk_score?.toFixed(1) || 0}</div>
                        <div class="text-sm text-gray-600">Risk Score (0-100)</div>
                    </div>
                </div>

                ${riskFactors.length > 0 ? `
                    <div class="mb-4">
                        <h4 class="text-sm font-medium text-gray-700 mb-2">Risk Factors</h4>
                        <ul class="space-y-1">
                            ${riskFactors.map(factor => `<li class="text-sm text-gray-600 flex items-start">
                                <i class="fas fa-exclamation-circle text-yellow-500 mr-2 mt-0.5 flex-shrink-0"></i>
                                ${factor}
                            </li>`).join('')}
                        </ul>
                    </div>
                ` : ''}

                ${recommendations.length > 0 ? `
                    <div>
                        <h4 class="text-sm font-medium text-gray-700 mb-2">Recommendations</h4>
                        <ul class="space-y-1">
                            ${recommendations.slice(0, 3).map(rec => `<li class="text-sm text-gray-600 flex items-start">
                                <i class="fas fa-lightbulb text-blue-500 mr-2 mt-0.5 flex-shrink-0"></i>
                                ${rec}
                            </li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            `;
        }

        function updateRecommendations() {
            const container = document.getElementById('recommendations-content');

            // Combine AI recommendations with general recommendations
            const aiRecs = dashboardData.ai_insights?.recommendations || [];
            const generalRecs = [
                "Implement regular financial performance reviews",
                "Set up automated KPI monitoring and alerting",
                "Develop comprehensive financial forecasting models",
                "Create detailed customer segmentation analysis"
            ];

            const allRecs = [...new Set([...aiRecs, ...generalRecs])];

            if (allRecs.length === 0) {
                container.innerHTML = `
                    <div class="text-center py-8 col-span-2">
                        <i class="fas fa-lightbulb text-gray-400 text-3xl mb-2"></i>
                        <p class="text-gray-600">No specific recommendations at this time</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = allRecs.map(rec => `
                <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div class="flex items-start">
                        <i class="fas fa-lightbulb text-yellow-600 mr-3 mt-1 flex-shrink-0"></i>
                        <p class="text-sm text-gray-800">${rec}</p>
                    </div>
                </div>
            `).join('');
        }

        function exportReport() {
            fetch('/api/export-report')
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                })
                .catch(error => {
                    console.error('Export error:', error);
                    alert('Failed to export report');
                });
        }

        // Utility functions
        function formatCurrency(amount) {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(amount);
        }

        function getAlertStyle(type) {
            const styles = {
                'warning': 'border-yellow-400 bg-yellow-50',
                'success': 'border-green-400 bg-green-50',
                'critical': 'border-red-400 bg-red-50',
                'info': 'border-blue-400 bg-blue-50'
            };
            return styles[type] || styles.info;
        }

        function getAlertIcon(type) {
            const icons = {
                'warning': 'fa-exclamation-triangle text-yellow-600',
                'success': 'fa-check-circle text-green-600',
                'critical': 'fa-times-circle text-red-600',
                'info': 'fa-info-circle text-blue-600'
            };
            return icons[type] || icons.info;
        }

        function getSeverityStyle(severity) {
            const styles = {
                'high': 'bg-red-100 text-red-800',
                'medium': 'bg-yellow-100 text-yellow-800',
                'low': 'bg-green-100 text-green-800'
            };
            return styles[severity] || styles.low;
        }

        function getRiskColor(level) {
            const colors = {
                'Low': 'text-green-600',
                'Medium': 'text-yellow-600',
                'High': 'text-red-600'
            };
            return colors[level] || colors.Low;
        }

        function getRiskBadgeColor(level) {
            const colors = {
                'Low': 'bg-green-100 text-green-800',
                'Medium': 'bg-yellow-100 text-yellow-800',
                'High': 'bg-red-100 text-red-800'
            };
            return colors[level] || colors.Low;
        }

        function showLoading() {
            document.getElementById('loading').classList.remove('hidden');
            document.getElementById('dashboard-content').classList.add('hidden');
        }

        function hideLoading() {
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('dashboard-content').classList.remove('hidden');
        }

        function showError(message) {
            const container = document.getElementById('dashboard-content');
            container.innerHTML = `
                <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                    <i class="fas fa-exclamation-triangle text-red-500 text-3xl mb-4"></i>
                    <h3 class="text-lg font-medium text-red-800 mb-2">Error Loading Dashboard</h3>
                    <p class="text-red-600">${message}</p>
                    <button onclick="loadDashboardData()" class="mt-4 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md">
                        <i class="fas fa-redo mr-2"></i>Retry
                    </button>
                </div>
            `;
            hideLoading();
        }
    </script>
</body>
</html>
        """

    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = True):
        """Run the dashboard server"""
        print(f"🚀 Starting Financial Excellence Dashboard on http://{host}:{port}")
        print("📊 Features:")
        print("   • Real-time financial metrics")
        print("   • AI-powered forecasting")
        print("   • Risk analysis and alerts")
        print("   • Interactive charts and visualizations")
        print("   • Comprehensive reporting")

        self.app.run(host=host, port=port, debug=debug)

# Example usage
if __name__ == '__main__':
    # Initialize the analytics engine
    tracker = AdvancedRevenueTracker()

    # Add some sample data for demonstration
    sample_data = [
        ("Consulting Services", 5000.00, RevenueCategory.SERVICES, datetime.utcnow() - timedelta(days=10)),
        ("Software License", 2500.00, RevenueCategory.SUBSCRIPTIONS, datetime.utcnow() - timedelta(days=8)),
        ("Investment Returns", 1200.00, RevenueCategory.INVESTMENTS, datetime.utcnow() - timedelta(days=5)),
        ("Product Sales", 3200.00, RevenueCategory.SALES, datetime.utcnow() - timedelta(days=3)),
        ("Consulting Services", 4800.00, RevenueCategory.SERVICES, datetime.utcnow() - timedelta(days=1)),
    ]

    for description, amount, category, date in sample_data:
        tracker.add_record(description, amount, category, date)

    # Create and run the dashboard
    dashboard = FinancialExcellenceDashboard(tracker)
    dashboard.run()
