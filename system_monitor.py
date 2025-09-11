#!/usr/bin/env python3
"""
System Monitoring Script for OWLban Group Integrated Application

This script provides comprehensive monitoring including:
- System health checks
- Performance metrics collection
- Alert generation and notification
- Resource usage monitoring
- Service availability checks

Usage:
    python system_monitor.py start
    python system_monitor.py status
    python system_monitor.py alerts
    python system_monitor.py metrics
"""

import subprocess
import sys
import logging
import json
import psutil
import time
from datetime import datetime
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

class SystemMonitor:
    def __init__(self):
        self.alerts = []
        self.metrics = {}

    def check_cpu_usage(self):
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics['cpu_usage'] = cpu_percent
        if cpu_percent > 90:
            self.alerts.append(f"High CPU usage: {cpu_percent}%")
        return cpu_percent

    def check_memory_usage(self):
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        self.metrics['memory_usage'] = memory_percent
        if memory_percent > 85:
            self.alerts.append(f"High memory usage: {memory_percent}%")
        return memory_percent

    def check_disk_usage(self):
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        self.metrics['disk_usage'] = disk_percent
        if disk_percent > 90:
            self.alerts.append(f"High disk usage: {disk_percent}%")
        return disk_percent

    def check_network_connections(self):
        connections = psutil.net_connections()
        active_connections = len([c for c in connections if c.status == 'ESTABLISHED'])
        self.metrics['active_connections'] = active_connections
        return active_connections

    def check_service_health(self, service_name, port):
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            is_healthy = result == 0
            self.metrics[f'{service_name}_health'] = is_healthy
            if not is_healthy:
                self.alerts.append(f"Service {service_name} is not responding on port {port}")
            return is_healthy
        except Exception as e:
            self.alerts.append(f"Error checking {service_name}: {str(e)}")
            return False

    def check_application_health(self):
        # Check Flask application
        flask_healthy = self.check_service_health('flask_app', 5000)

        # Check database connection
        try:
            # Add database health check logic here
            db_healthy = True
            self.metrics['database_health'] = db_healthy
        except Exception as e:
            db_healthy = False
            self.alerts.append(f"Database health check failed: {str(e)}")

        return flask_healthy and db_healthy

    def collect_metrics(self):
        logging.info("Collecting system metrics...")
        self.check_cpu_usage()
        self.check_memory_usage()
        self.check_disk_usage()
        self.check_network_connections()
        self.check_application_health()

        timestamp = datetime.now().isoformat()
        metrics_data = {
            'timestamp': timestamp,
            'metrics': self.metrics,
            'alerts': self.alerts
        }

        # Save metrics to file
        with open(f'metrics_{timestamp.replace(":", "-")}.json', 'w') as f:
            json.dump(metrics_data, f, indent=2)

        return metrics_data

    def send_alerts(self):
        if self.alerts:
            logging.warning(f"Sending {len(self.alerts)} alerts...")
            for alert in self.alerts:
                logging.warning(f"ALERT: {alert}")
            # Here you could integrate with email, Slack, etc.
        else:
            logging.info("No alerts to send.")

    def display_status(self):
        print("\n=== System Status ===")
        print(f"CPU Usage: {self.metrics.get('cpu_usage', 'N/A')}%")
        print(f"Memory Usage: {self.metrics.get('memory_usage', 'N/A')}%")
        print(f"Disk Usage: {self.metrics.get('disk_usage', 'N/A')}%")
        print(f"Active Connections: {self.metrics.get('active_connections', 'N/A')}")
        print(f"Flask App Health: {self.metrics.get('flask_app_health', 'N/A')}")
        print(f"Database Health: {self.metrics.get('database_health', 'N/A')}")

        if self.alerts:
            print("\n=== Active Alerts ===")
            for alert in self.alerts:
                print(f"⚠️  {alert}")
        else:
            print("\n✅ No active alerts")

def run_command(command, check=True):
    logging.info(f"Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        logging.info(f"Output: {result.stdout.strip()}")
    if result.stderr:
        logging.error(f"Error: {result.stderr.strip()}")
    if check and result.returncode != 0:
        logging.error(f"Command failed with exit code {result.returncode}")
        return False
    return True

def start_monitoring():
    monitor = SystemMonitor()
    logging.info("Starting system monitoring...")

    try:
        while True:
            monitor.collect_metrics()
            monitor.send_alerts()
            monitor.display_status()
            time.sleep(60)  # Monitor every minute
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user.")

def check_status():
    monitor = SystemMonitor()
    metrics = monitor.collect_metrics()
    monitor.display_status()
    return metrics

def show_alerts():
    monitor = SystemMonitor()
    monitor.collect_metrics()
    monitor.send_alerts()

def show_metrics():
    monitor = SystemMonitor()
    metrics = monitor.collect_metrics()
    print(json.dumps(metrics, indent=2))

def main():
    if len(sys.argv) < 2:
        logging.error("No command provided. Use 'start', 'status', 'alerts', or 'metrics'.")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "start":
        start_monitoring()
    elif command == "status":
        check_status()
    elif command == "alerts":
        show_alerts()
    elif command == "metrics":
        show_metrics()
    else:
        logging.error(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
