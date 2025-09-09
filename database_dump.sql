-- OSCAR-BROOME-REVENUE Database Dump with Seed Data
-- Generated for production deployment
-- Version: 1.0.0
-- Generated: 2024-12-19

-- =====================================================
-- DATABASE SCHEMA AND SEED DATA
-- =====================================================

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS owlban_db;
USE owlban_db;

-- =====================================================
-- USERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'manager', 'user') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert seed users
INSERT INTO users (username, email, password_hash, role, is_active, mfa_enabled) VALUES
('admin', 'admin@oscar-broome.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPjYLC2s/zFe', 'admin', TRUE, TRUE),
('manager1', 'manager1@oscar-broome.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPjYLC2s/zFe', 'manager', TRUE, FALSE),
('user1', 'user1@oscar-broome.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPjYLC2s/zFe', 'user', TRUE, FALSE);

-- =====================================================
-- REVENUE DATA TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS revenue_data (
    id SERIAL PRIMARY KEY,
    total_revenue DECIMAL(15,2) DEFAULT 0.00,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    revenue_streams JSON,
    purchases JSON,
    payroll_total DECIMAL(12,2) DEFAULT 0.00,
    audit_trail JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_period (period_start, period_end)
);

-- Insert seed revenue data
INSERT INTO revenue_data (total_revenue, period_start, period_end, revenue_streams, purchases, payroll_total) VALUES
(1500000.00, '2024-01-01', '2024-01-31',
 '{
   "corporate_housing": 750000.00,
   "auto_fleet": 450000.00,
   "financial_services": 300000.00
 }',
 '{
   "corporateHomes": 2,
   "corporateHomesDetails": [
     {"model": "Executive Suite A", "cost": 250000.00, "purchaseDate": "2024-01-15"},
     {"model": "Executive Suite B", "cost": 180000.00, "purchaseDate": "2024-01-20"}
   ],
   "autoFleet": 5,
   "autoFleetDetails": [
     {"model": "Luxury Sedan", "vin": "1HGCM82633A123456", "cost": 85000.00, "purchaseDate": "2024-01-10"},
     {"model": "SUV Executive", "vin": "2T1BURHE0EC123456", "cost": 95000.00, "purchaseDate": "2024-01-12"}
   ]
 }',
 125000.00
),
(1650000.00, '2024-02-01', '2024-02-29',
 '{
   "corporate_housing": 825000.00,
   "auto_fleet": 495000.00,
   "financial_services": 330000.00
 }',
 '{
   "corporateHomes": 1,
   "corporateHomesDetails": [
     {"model": "Premium Office Space", "cost": 320000.00, "purchaseDate": "2024-02-08"}
   ],
   "autoFleet": 3,
   "autoFleetDetails": [
     {"model": "Electric Luxury", "vin": "5YJ3E1EA0KF123456", "cost": 120000.00, "purchaseDate": "2024-02-05"}
   ]
 }',
 132000.00
);

-- =====================================================
-- PAYROLL DATA TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS payroll_data (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    employee_name VARCHAR(100) NOT NULL,
    department VARCHAR(50),
    salary DECIMAL(10,2) NOT NULL,
    bonus DECIMAL(8,2) DEFAULT 0.00,
    deductions DECIMAL(8,2) DEFAULT 0.00,
    net_pay DECIMAL(10,2) NOT NULL,
    pay_period_start DATE NOT NULL,
    pay_period_end DATE NOT NULL,
    payment_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert seed payroll data
INSERT INTO payroll_data (employee_id, employee_name, department, salary, bonus, deductions, net_pay, pay_period_start, pay_period_end, payment_date) VALUES
('EMP001', 'John Smith', 'Executive', 150000.00, 25000.00, 15000.00, 160000.00, '2024-01-01', '2024-01-15', '2024-01-16'),
('EMP002', 'Sarah Johnson', 'Finance', 120000.00, 15000.00, 12000.00, 123000.00, '2024-01-01', '2024-01-15', '2024-01-16'),
('EMP003', 'Michael Brown', 'Operations', 95000.00, 10000.00, 9500.00, 100500.00, '2024-01-01', '2024-01-15', '2024-01-16'),
('EMP004', 'Emily Davis', 'HR', 85000.00, 8000.00, 8500.00, 88500.00, '2024-01-01', '2024-01-15', '2024-01-16'),
('EMP005', 'David Wilson', 'IT', 110000.00, 12000.00, 11000.00, 112000.00, '2024-01-01', '2024-01-15', '2024-01-16');

-- =====================================================
-- AUTHENTICATION LOGS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS auth_logs (
    id SERIAL PRIMARY KEY,
    user_id INT,
    action VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN DEFAULT FALSE,
    failure_reason VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Insert seed auth logs
INSERT INTO auth_logs (user_id, action, ip_address, success, timestamp) VALUES
(1, 'login', '192.168.1.100', TRUE, '2024-12-19 09:00:00'),
(2, 'login', '192.168.1.101', TRUE, '2024-12-19 09:15:00'),
(1, 'password_change', '192.168.1.100', TRUE, '2024-12-19 10:00:00');

-- =====================================================
-- API LOGS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS api_logs (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INT NOT NULL,
    response_time_ms INT,
    user_id INT,
    ip_address VARCHAR(45),
    request_body JSON,
    response_body JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Insert seed API logs
INSERT INTO api_logs (endpoint, method, status_code, response_time_ms, user_id, ip_address, timestamp) VALUES
('/api/earnings', 'GET', 200, 150, 1, '192.168.1.100', '2024-12-19 09:05:00'),
('/api/payroll', 'GET', 200, 200, 2, '192.168.1.101', '2024-12-19 09:20:00'),
('/api/financial-excellence', 'POST', 201, 300, 1, '192.168.1.100', '2024-12-19 10:05:00');

-- =====================================================
-- JPMORGAN PAYMENT LOGS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS jpmorgan_payments (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status ENUM('pending', 'completed', 'failed', 'cancelled') DEFAULT 'pending',
    payment_method VARCHAR(50),
    recipient_account VARCHAR(100),
    sender_account VARCHAR(100),
    description TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert seed JPMorgan payment data
INSERT INTO jpmorgan_payments (transaction_id, amount, status, payment_method, recipient_account, description) VALUES
('JPM_TXN_001', 50000.00, 'completed', 'wire_transfer', 'ACC123456789', 'Corporate housing payment'),
('JPM_TXN_002', 25000.00, 'completed', 'ach', 'ACC987654321', 'Auto fleet maintenance'),
('JPM_TXN_003', 100000.00, 'pending', 'wire_transfer', 'ACC456789123', 'Executive bonus payment');

-- =====================================================
-- NVIDIA INTEGRATION LOGS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS nvidia_logs (
    id SERIAL PRIMARY KEY,
    gpu_id VARCHAR(50),
    action VARCHAR(100) NOT NULL,
    parameters JSON,
    result JSON,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    execution_time_ms INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert seed NVIDIA logs
INSERT INTO nvidia_logs (gpu_id, action, parameters, result, success, execution_time_ms) VALUES
('GPU_001', 'gpu_optimization', '{"resolution": "4K", "refresh_rate": 144}', '{"performance_gain": 15}', TRUE, 500),
('GPU_002', 'driver_update', '{"version": "550.54.14"}', '{"update_successful": true}', TRUE, 3000),
('GPU_001', 'power_management', '{"mode": "performance"}', '{"power_savings": 10}', TRUE, 200);

-- =====================================================
-- SYSTEM HEALTH TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS system_health (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    status ENUM('healthy', 'warning', 'critical', 'down') DEFAULT 'healthy',
    cpu_usage DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    disk_usage DECIMAL(5,2),
    response_time_ms INT,
    error_count INT DEFAULT 0,
    uptime_seconds BIGINT,
    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSON
);

-- Insert seed system health data
INSERT INTO system_health (service_name, status, cpu_usage, memory_usage, response_time_ms, uptime_seconds) VALUES
('backend_api', 'healthy', 15.5, 45.2, 150, 86400),
('frontend_app', 'healthy', 8.3, 32.1, 200, 86400),
('database', 'healthy', 22.1, 68.5, 50, 86400),
('nvidia_service', 'healthy', 5.2, 15.8, 100, 86400);

-- =====================================================
-- AUDIT TRAIL TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS audit_trail (
    id SERIAL PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Insert seed audit trail data
INSERT INTO audit_trail (user_id, action, resource_type, resource_id, ip_address, timestamp) VALUES
(1, 'CREATE', 'revenue_data', '1', '192.168.1.100', '2024-12-19 09:00:00'),
(1, 'UPDATE', 'payroll_data', 'EMP001', '192.168.1.100', '2024-12-19 10:00:00'),
(2, 'VIEW', 'financial_report', 'Q1_2024', '192.168.1.101', '2024-12-19 11:00:00');

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================
CREATE INDEX idx_revenue_data_period ON revenue_data (period_start, period_end);
CREATE INDEX idx_payroll_employee ON payroll_data (employee_id, pay_period_start);
CREATE INDEX idx_auth_logs_user ON auth_logs (user_id, timestamp);
CREATE INDEX idx_api_logs_endpoint ON api_logs (endpoint, timestamp);
CREATE INDEX idx_audit_trail_user ON audit_trail (user_id, timestamp);
CREATE INDEX idx_system_health_service ON system_health (service_name, last_check);

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Monthly revenue summary view
CREATE OR REPLACE VIEW monthly_revenue_summary AS
SELECT
    DATE_FORMAT(period_start, '%Y-%m') as month,
    SUM(total_revenue) as total_revenue,
    SUM(payroll_total) as total_payroll,
    COUNT(*) as record_count
FROM revenue_data
GROUP BY DATE_FORMAT(period_start, '%Y-%m')
ORDER BY month DESC;

-- User activity summary view
CREATE OR REPLACE VIEW user_activity_summary AS
SELECT
    u.username,
    u.email,
    u.role,
    COUNT(al.id) as login_attempts,
    MAX(al.timestamp) as last_login,
    COUNT(DISTINCT DATE(al.timestamp)) as active_days
FROM users u
LEFT JOIN auth_logs al ON u.id = al.user_id AND al.action = 'login' AND al.success = TRUE
GROUP BY u.id, u.username, u.email, u.role;

-- System performance view
CREATE OR REPLACE VIEW system_performance AS
SELECT
    service_name,
    AVG(cpu_usage) as avg_cpu,
    AVG(memory_usage) as avg_memory,
    AVG(response_time_ms) as avg_response_time,
    MAX(last_check) as last_updated
FROM system_health
WHERE last_check >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY service_name;

-- =====================================================
-- STORED PROCEDURES
-- =====================================================

DELIMITER //

-- Procedure to generate monthly financial report
CREATE PROCEDURE generate_monthly_report(IN report_month DATE)
BEGIN
    SELECT
        rd.total_revenue,
        rd.payroll_total,
        rd.total_revenue - rd.payroll_total as net_profit,
        JSON_EXTRACT(rd.revenue_streams, '$.corporate_housing') as corporate_housing_revenue,
        JSON_EXTRACT(rd.revenue_streams, '$.auto_fleet') as auto_fleet_revenue,
        JSON_EXTRACT(rd.purchases, '$.corporateHomes') as corporate_homes_purchased,
        JSON_EXTRACT(rd.purchases, '$.autoFleet') as auto_fleet_purchased
    FROM revenue_data rd
    WHERE DATE_FORMAT(rd.period_start, '%Y-%m') = DATE_FORMAT(report_month, '%Y-%m');
END //

-- Procedure to cleanup old logs
CREATE PROCEDURE cleanup_old_logs(IN days_old INT)
BEGIN
    DELETE FROM auth_logs WHERE timestamp < DATE_SUB(NOW(), INTERVAL days_old DAY);
    DELETE FROM api_logs WHERE timestamp < DATE_SUB(NOW(), INTERVAL days_old DAY);
    DELETE FROM audit_trail WHERE timestamp < DATE_SUB(NOW(), INTERVAL days_old DAY);
END //

DELIMITER ;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger to update updated_at timestamp
DELIMITER //

CREATE TRIGGER update_revenue_data_timestamp
    BEFORE UPDATE ON revenue_data
    FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END //

CREATE TRIGGER update_jpmorgan_payments_timestamp
    BEFORE UPDATE ON jpmorgan_payments
    FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END //

DELIMITER ;

-- =====================================================
-- DATABASE CONFIGURATION
-- =====================================================

-- Set timezone
SET time_zone = '+00:00';

-- Configure connection settings
SET GLOBAL max_connections = 1000;
SET GLOBAL innodb_buffer_pool_size = 1073741824; -- 1GB
SET GLOBAL innodb_log_file_size = 268435456; -- 256MB

-- =====================================================
-- END OF DATABASE DUMP
-- =====================================================

-- Note: Default passwords for seed users are 'password123'
-- Please change these in production environment
-- Admin password hash corresponds to 'admin123'
-- Manager/User password hash corresponds to 'password123'

COMMIT;
