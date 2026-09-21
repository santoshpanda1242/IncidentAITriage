-- MySQL Database Setup for Incident Triage System
-- This creates the database structure and sample data

-- Create Database
CREATE DATABASE IF NOT EXISTS incident_logs;
USE incident_logs;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS error_logs;
DROP TABLE IF EXISTS incidents;
DROP TABLE IF EXISTS services;

-- Create Services Table
CREATE TABLE services (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL UNIQUE,
    version VARCHAR(50),
    environment ENUM('production', 'staging', 'development'),
    team VARCHAR(50),
    criticality ENUM('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'),
    dependencies TEXT,
    sla_target VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create Error Logs Table
CREATE TABLE error_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    error_code VARCHAR(50),
    error_message TEXT NOT NULL,
    severity ENUM('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    stack_trace TEXT,
    affected_components TEXT,
    user_impact INT DEFAULT 0,
    resolution_status ENUM('OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED') DEFAULT 'OPEN',
    FOREIGN KEY (service_name) REFERENCES services(service_name) ON DELETE CASCADE
);

-- Create Incidents Table
CREATE TABLE incidents (
    incident_id VARCHAR(50) PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    severity ENUM('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'),
    status ENUM('OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED') DEFAULT 'OPEN',
    affected_users INT DEFAULT 0,
    business_impact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    assigned_to VARCHAR(100),
    incident_type ENUM('OUTAGE', 'DEGRADATION', 'DATA_LOSS', 'SECURITY', 'PERFORMANCE'),
    root_cause_category ENUM('HARDWARE', 'SOFTWARE', 'NETWORK', 'HUMAN_ERROR', 'EXTERNAL', 'UNKNOWN', 'PERFORMANCE'),
    resolution_notes TEXT,
    mitigation_steps TEXT,
   FOREIGN KEY (service_name) REFERENCES services(service_name) ON DELETE CASCADE
);

-- Insert Sample Services
INSERT INTO services (service_name, version, environment, team, criticality, dependencies, sla_target) VALUES
('payment-service', '2.3.1', 'production', 'payments', 'HIGH', 'database,cache,api-gateway,payment-gateway,fraud-detection', '99.9%'),
('user-service', '1.8.4', 'production', 'identity', 'MEDIUM', 'database,auth-service,ldap,session-store', '99.5%'),
('notification-service', '3.0.0', 'staging', 'communications', 'LOW', 'message-queue,email-provider,sms-gateway,push-service', '99.0%'),
('order-service', '4.2.0', 'production', 'ecommerce', 'HIGH', 'database,inventory-service,payment-service,shipping-service', '99.9%'),
('analytics-service', '2.1.3', 'production', 'data', 'MEDIUM', 'database,data-warehouse,spark,kafka', '99.5%'),
('file-upload-service', '1.5.2', 'production', 'storage', 'HIGH', 's3,cdn,compression-service,antivirus,thumbnail-generator', '99.8%'),
('search-service', '3.4.1', 'production', 'discovery', 'MEDIUM', 'elasticsearch,cache,database,autocomplete-service', '99.7%'),
('auth-service', '2.0.0', 'production', 'security', 'HIGH', 'database,ldap,oauth-provider,mfa-service,jwt-validator', '99.9%'),
('recommendation-service', '1.2.0', 'production', 'ml', 'MEDIUM', 'database,redis,ml-model-api,tracking-service', '99.5%'),
('reporting-service', '2.8.1', 'production', 'business-intelligence', 'LOW', 'database,data-warehouse,export-service,email-service', '99.0%'),
('api-gateway', '3.5.0', 'production', 'platform', 'CRITICAL', 'load-balancer,rate-limiter,auth-service,monitoring', '99.95%'),
('cache-service', '1.9.2', 'production', 'infrastructure', 'HIGH', 'redis-cluster,monitoring,backup-service', '99.9%'),
('database-service', '2.4.0', 'production', 'database', 'CRITICAL', 'mysql-cluster,replication-manager,backup-service,monitoring', '99.95%'),
('cdn-service', '2.1.0', 'production', 'infrastructure', 'MEDIUM', 'cloudflare-provider,origin-server,cache-invalidation', '99.8%'),
('workflow-service', '1.6.3', 'production', 'operations', 'MEDIUM', 'database,message-queue,task-scheduler,notification-service', '99.5%'),
('integration-service', '2.3.1', 'production', 'integrations', 'HIGH', 'database,api-client,transform-service,error-handler', '99.7%');

-- Insert Sample Error Logs - Multiple Cases and Issues (Extended and Complex)

-- Payment Service Issues (Extended)
INSERT INTO error_logs (service_name, error_code, error_message, severity, stack_trace, affected_components, user_impact) VALUES
('payment-service', 'ERR-5001', 'Database connection timeout during payment processing', 'CRITICAL', 'at db.connect() line 45\nat payment.process() line 120', 'database,payment-gateway', 1500),
('payment-service', 'ERR-5002', 'Payment gateway API rate limit exceeded', 'HIGH', 'at gateway.request() line 78\nat payment.process() line 130', 'payment-gateway,api', 800),
('payment-service', 'ERR-5003', 'Transaction deadlock detected', 'HIGH', 'at db.transaction() line 89\nat payment.process() line 115', 'database', 200),
('payment-service', 'WARN-1001', 'High memory usage in payment processing', 'MEDIUM', 'at memory.check() line 45', 'cache,payment-worker', 0),
('payment-service', 'ERR-5004', 'SSL certificate validation failed for payment gateway', 'CRITICAL', 'at ssl.validate() line 23\nat gateway.connect() line 56', 'payment-gateway,network', 2500),
('payment-service', 'ERR-5005', 'Fraud detection service timeout during high-risk transaction', 'HIGH', 'at fraud.check() line 234\nat payment.validate() line 89', 'fraud-detection,api', 450),
('payment-service', 'ERR-5006', 'Currency conversion API unavailable for international payments', 'MEDIUM', 'at currency.convert() line 123\nat payment.process() line 167', 'currency-api,external-service', 300),
('payment-service', 'WARN-1002', 'Payment reconciliation job failed to process batch', 'MEDIUM', 'at reconciliation.process_batch() line 345', 'database,worker', 0),
('payment-service', 'ERR-5007', '3D Secure authentication flow interrupted', 'HIGH', 'at secure3d.authenticate() line 156\nat payment.process() line 234', 'payment-gateway,authentication', 600),
('payment-service', 'ERR-5008', 'Recurring payment billing cycle processing failed', 'CRITICAL', 'at billing.process_cycle() line 78\nat payment.recurring() line 123', 'database,payment-gateway', 1200);

-- User Service Issues (Extended)
INSERT INTO error_logs (service_name, error_code, error_message, severity, stack_trace, affected_components, user_impact) VALUES
('user-service', 'ERR-3001', 'LDAP connection timeout during authentication', 'HIGH', 'at ldap.connect() line 34\nat auth.authenticate() line 67', 'ldap,auth-service', 5000),
('user-service', 'ERR-3002', 'User profile data corruption detected', 'CRITICAL', 'at db.query() line 156\nat profile.load() line 89', 'database', 1200),
('user-service', 'WARN-2001', 'Slow query performance on user lookups', 'MEDIUM', 'at db.query() line 234\nat user.search() line 45', 'database,cache', 0),
('user-service', 'ERR-3003', 'Session store connection failed', 'HIGH', 'at redis.connect() line 12\nat session.create() line 78', 'cache,session-manager', 3000),
('user-service', 'INFO-1001', 'Password reset token expired', 'INFO', 'at token.validate() line 45', 'auth-service', 50),
('user-service', 'ERR-3004', 'User permission sync failed with external systems', 'MEDIUM', 'at sync.permissions() line 234\nat user.update() line 123', 'external-api,database', 800),
('user-service', 'WARN-2002', 'Account lockout threshold exceeded for multiple users', 'HIGH', 'at security.check_lockout() line 89', 'auth-service,security', 1500),
('user-service', 'ERR-3005', 'Profile image upload processing failed', 'MEDIUM', 'at image.process() line 156\nat profile.update() line 234', 'file-service,cdn', 400),
('user-service', 'ERR-3006', 'Email verification service unavailable for new registrations', 'HIGH', 'at email.verify() line 67\nat user.register() line 123', 'email-service,api', 2500),
('user-service', 'WARN-2003', 'User activity tracking data inconsistency detected', 'LOW', 'at tracking.validate() line 45', 'database,analytics', 0);

-- Notification Service Issues (Extended)
INSERT INTO error_logs (service_name, error_code, error_message, severity, stack_trace, affected_components, user_impact) VALUES
('notification-service', 'ERR-4001', 'Email provider API authentication failed', 'HIGH', 'at smtp.auth() line 67\nat email.send() line 123', 'email-provider,api', 200),
('notification-service', 'ERR-4002', 'Message queue connection lost', 'CRITICAL', 'at mq.connect() line 34\nat queue.publish() line 89', 'message-queue,network', 500),
('notification-service', 'WARN-3001', 'SMS gateway rate limit approaching', 'MEDIUM', 'at sms.check_rate() line 56', 'sms-gateway', 0),
('notification-service', 'ERR-4003', 'Template rendering failed for notification', 'MEDIUM', 'at template.render() line 78\nat notification.build() line 45', 'template-engine', 100),
('notification-service', 'ERR-4004', 'Push notification service connection timeout', 'HIGH', 'at push.connect() line 123\nat notification.send() line 234', 'push-service,api', 800),
('notification-service', 'WARN-3002', 'Notification delivery queue backlog increasing', 'MEDIUM', 'at queue.check_backlog() line 89', 'message-queue,worker', 0),
('notification-service', 'ERR-4005', 'Notification preference sync failed for user batch', 'MEDIUM', 'at preferences.sync() line 156\nat notification.target() line 67', 'database,cache', 300),
('notification-service', 'ERR-4006', 'Webhook delivery failed for external integrations', 'HIGH', 'at webhook.deliver() line 234\nat notification.send() line 345', 'webhook-service,external-api', 150);

-- Order Service Issues (Extended)
INSERT INTO error_logs (service_name, error_code, error_message, severity, stack_trace, affected_components, user_impact) VALUES
('order-service', 'ERR-6001', 'Inventory service unavailable during order creation', 'CRITICAL', 'at inventory.check() line 123\nat order.create() line 200', 'inventory-service,api', 3500),
('order-service', 'ERR-6002', 'Order processing pipeline timeout', 'HIGH', 'at pipeline.execute() line 156\nat order.process() line 89', 'pipeline,worker', 1800),
('order-service', 'ERR-6003', 'Payment callback handling failed', 'HIGH', 'at payment.callback() line 234\nat order.update() line 145', 'payment-service,webhook', 900),
('order-service', 'WARN-4001', 'Order index synchronization delay', 'LOW', 'at search.sync() line 67', 'search-service,database', 0),
('order-service', 'ERR-6004', 'Shipping service integration timeout during order fulfillment', 'HIGH', 'at shipping.get_rates() line 234\nat order.fulfill() line 167', 'shipping-service,api', 1200),
('order-service', 'ERR-6005', 'Order modification validation failed for existing orders', 'MEDIUM', 'at validation.modify() line 89\nat order.update() line 123', 'validation,database', 600),
('order-service', 'WARN-4002', 'Order analytics data aggregation delayed', 'LOW', 'at analytics.aggregate() line 156', 'analytics-service,database', 0),
('order-service', 'ERR-6006', 'Coupon code validation service unavailable', 'MEDIUM', 'at coupon.validate() line 234\nat order.apply_discount() line 89', 'coupon-service,api', 450),
('order-service', 'ERR-6007', 'Multi-warehouse inventory sync failed', 'HIGH', 'at inventory.sync() line 345\nat order.allocate() line 234', 'inventory-service,database', 1800),
('order-service', 'WARN-4003', 'Order export to external ERP system failed', 'MEDIUM', 'at erp.export() line 123', 'erp-service,external-api', 0);

-- Analytics Service Issues (Extended)
INSERT INTO error_logs (service_name, error_code, error_message, severity, stack_trace, affected_components, user_impact) VALUES
('analytics-service', 'ERR-7001', 'Data warehouse connection pool exhausted', 'HIGH', 'at pool.get_connection() line 45\nat warehouse.query() line 123', 'data-warehouse,connection-pool', 0),
('analytics-service', 'ERR-7002', 'Spark job execution failed', 'MEDIUM', 'at spark.submit() line 234\nat analytics.process() line 89', 'spark,cluster', 0),
('analytics-service', 'WARN-5001', 'Aggregation query performance degradation', 'MEDIUM', 'at query.aggregate() line 156', 'database,cache', 0),
('analytics-service', 'ERR-7003', 'Kafka consumer lag detected for real-time analytics', 'HIGH', 'at kafka.consume() line 123\nat analytics.stream() line 234', 'kafka,stream-processor', 0),
('analytics-service', 'ERR-7004', 'Data quality validation failed for daily batch', 'MEDIUM', 'at quality.validate() line 89\nat analytics.batch() line 156', 'validation,database', 0),
('analytics-service', 'WARN-5002', 'Analytics dashboard cache refresh failed', 'LOW', 'at cache.refresh() line 234', 'cache,dashboard', 0),
('analytics-service', 'ERR-7005', 'Custom report generation timeout for large datasets', 'MEDIUM', 'at report.generate() line 345\nat analytics.custom() line 123', 'reporting-engine,worker', 0),
('analytics-service', 'ERR-7006', 'Data retention policy cleanup job failed', 'LOW', 'at retention.cleanup() line 67', 'database,worker', 0);

-- File Upload Service Issues (Extended)
INSERT INTO error_logs (service_name, error_code, error_message, severity, stack_trace, affected_components, user_impact) VALUES
('file-upload-service', 'ERR-8001', 'S3 upload connection timeout', 'CRITICAL', 'at s3.upload() line 78\nat file.process() line 145', 's3,network', 4000),
('file-upload-service', 'ERR-8002', 'File size validation failed', 'MEDIUM', 'at validation.check_size() line 34\nat file.validate() line 56', 'validation,api', 300),
('file-upload-service', 'ERR-8003', 'Virus scan service unavailable', 'HIGH', 'at antivirus.scan() line 123\nat file.process() line 167', 'antivirus,api', 800),
('file-upload-service', 'WARN-6001', 'CDN cache invalidation delay', 'LOW', 'at cdn.invalidate() line 89', 'cdn,cache', 0),
('file-upload-service', 'ERR-8004', 'Thumbnail generation failed for image upload', 'MEDIUM', 'at thumbnail.generate() line 234\nat file.process() line 345', 'thumbnail-service,worker', 200),
('file-upload-service', 'ERR-8005', 'File compression service timeout for large files', 'HIGH', 'at compression.compress() line 156\nat file.process() line 234', 'compression-service,worker', 500),
('file-upload-service', 'WARN-6002', 'File metadata extraction failed for PDF documents', 'LOW', 'at metadata.extract() line 89', 'metadata-service,worker', 0),
('file-upload-service', 'ERR-8006', 'Upload progress tracking synchronization failed', 'MEDIUM', 'at progress.sync() line 123\nat file.upload() line 234', 'cache,websocket', 150),
('file-upload-service', 'ERR-8007', 'Storage quota exceeded for user account', 'MEDIUM', 'at quota.check() line 67\nat file.validate() line 89', 'database,storage-service', 400);

-- Search Service Issues (Extended)
INSERT INTO error_logs (service_name, error_code, error_message, severity, stack_trace, affected_components, user_impact) VALUES
('search-service', 'ERR-9001', 'Elasticsearch cluster health degraded', 'HIGH', 'at es.health_check() line 45\nat search.query() line 234', 'elasticsearch,cluster', 2000),
('search-service', 'ERR-9002', 'Search index rebuild failed', 'CRITICAL', 'at index.rebuild() line 156\nat search.update() line 89', 'elasticsearch,worker', 0),
('search-service', 'WARN-7001', 'Search query latency increased', 'MEDIUM', 'at query.execute() line 123', 'elasticsearch,cache', 500),
('search-service', 'ERR-9003', 'Autocomplete service integration timeout', 'HIGH', 'at autocomplete.suggest() line 234\nat search.typeahead() line 167', 'autocomplete-service,api', 800),
('search-service', 'ERR-9004', 'Search result ranking algorithm update failed', 'MEDIUM', 'at ranking.update() line 345\nat search.rank() line 123', 'ranking-service,worker', 0),
('search-service', 'WARN-7002', 'Search analytics data collection delayed', 'LOW', 'at analytics.collect() line 89', 'analytics-service,database', 0),
('search-service', 'ERR-9005', 'Faceted search filter processing failed', 'MEDIUM', 'at facets.process() line 156\nat search.filter() line 234', 'filter-service,cache', 300),
('search-service', 'ERR-9006', 'Search synonym dictionary sync failed', 'LOW', 'at synonym.sync() line 67', 'dictionary-service,api', 0);

-- Auth Service Issues (Extended)
INSERT INTO error_logs (service_name, error_code, error_message, severity, stack_trace, affected_components, user_impact) VALUES
('auth-service', 'ERR-10001', 'OAuth provider token endpoint unavailable', 'CRITICAL', 'at oauth.token() line 234\nat auth.authenticate() line 89', 'oauth-provider,api', 6000),
('auth-service', 'ERR-10002', 'JWT validation failed for expired tokens', 'HIGH', 'at jwt.validate() line 67\nat auth.verify() line 45', 'jwt,token-store', 4000),
('auth-service', 'WARN-8001', 'Multi-factor authentication service slow', 'MEDIUM', 'at mfa.verify() line 123', 'mfa-service,api', 1000),
('auth-service', 'ERR-10003', 'Permission cache invalidation failed after role update', 'HIGH', 'at cache.invalidate() line 234\nat auth.update_role() line 167', 'cache,database', 800),
('auth-service', 'ERR-10004', 'Single sign-on (SSO) integration timeout', 'CRITICAL', 'at sso.authenticate() line 345\nat auth.sso() line 123', 'sso-provider,api', 3500),
('auth-service', 'WARN-8002', 'Security audit log write failed', 'MEDIUM', 'at audit.log() line 89', 'audit-service,database', 0),
('auth-service', 'ERR-10005', 'API key rotation process failed for service accounts', 'HIGH', 'at key.rotate() line 156\nat auth.manage_keys() line 234', 'key-management,database', 0),
('auth-service', 'ERR-10006', 'Session timeout configuration sync failed across instances', 'MEDIUM', 'at config.sync() line 67\nat session.configure() line 123', 'config-service,cache', 500);

-- Additional Service Issues

-- Recommendation Service Issues
INSERT INTO error_logs (service_name, error_code, error_message, severity, stack_trace, affected_components, user_impact) VALUES
('recommendation-service', 'ERR-11001', 'ML model API timeout during recommendation generation', 'HIGH', 'at ml.predict() line 234\nat recommendation.generate() line 123', 'ml-model-api,external-service', 0),
('recommendation-service', 'ERR-11002', 'User behavior tracking data incomplete', 'MEDIUM', 'at tracking.collect() line 156\nat recommendation.build_profile() line 89', 'tracking-service,database', 0),
('recommendation-service', 'WARN-9001', 'Recommendation cache hit rate below threshold', 'LOW', 'at cache.monitor() line 67', 'cache,monitoring', 0),
('recommendation-service', 'ERR-11003', 'A/B test configuration sync failed for recommendation algorithm', 'MEDIUM', 'at abtest.sync() line 234\nat recommendation.configure() line 167', 'abtest-service,config', 0);

-- Reporting Service Issues
INSERT INTO error_logs (service_name, error_code, error_message, severity, stack_trace, affected_components, user_impact) VALUES
('reporting-service', 'ERR-12001', 'Report export service timeout for large datasets', 'HIGH', 'at export.generate() line 345\nat report.create() line 234', 'export-service,worker', 0),
('reporting-service', 'ERR-12002', 'Scheduled report generation failed for daily batch', 'MEDIUM', 'at scheduler.execute() line 123\nat report.batch() line 89', 'scheduler,database', 0),
('reporting-service', 'WARN-10001', 'Report delivery queue backlog detected', 'LOW', 'at queue.check() line 67', 'message-queue,worker', 0),
('reporting-service', 'ERR-12003', 'Data visualization rendering failed for dashboard', 'MEDIUM', 'at visualization.render() line 234\nat report.build_dashboard() line 167', 'visualization-service,worker', 0);

-- API Gateway Issues
INSERT INTO error_logs (service_name, error_code, error_message, severity, stack_trace, affected_components, user_impact) VALUES
('api-gateway', 'ERR-13001', 'Rate limiter configuration sync failed across instances', 'HIGH', 'at ratelimit.sync() line 234\nat gateway.configure() line 123', 'rate-limiter,config-service', 5000),
('api-gateway', 'ERR-13002', 'Load balancer health check failed for backend service', 'CRITICAL', 'at loadbalancer.health_check() line 345\nat gateway.route() line 167', 'load-balancer,network', 8000),
('api-gateway', 'WARN-11001', 'API request latency increased above SLA threshold', 'HIGH', 'at monitoring.check_latency() line 89', 'monitoring,performance', 0),
('api-gateway', 'ERR-13003', 'Circuit breaker triggered for failing backend service', 'HIGH', 'at circuitbreaker.trip() line 156\nat gateway.handle_failure() line 234', 'circuit-breaker,backend-service', 3000),
('api-gateway', 'ERR-13004', 'API version compatibility validation failed', 'MEDIUM', 'at version.validate() line 67\nat gateway.route() line 123', 'versioning,validation', 1200);

-- Cache Service Issues
INSERT INTO error_logs (service_name, error_code, error_message, severity, stack_trace, affected_components, user_impact) VALUES
('cache-service', 'ERR-14001', 'Redis cluster node failure detected', 'CRITICAL', 'at redis.cluster_check() line 234\nat cache.monitor() line 123', 'redis-cluster,monitoring', 0),
('cache-service', 'ERR-14002', 'Cache eviction policy misconfiguration causing data loss', 'HIGH', 'at cache.configure_eviction() line 156\nat cache.setup() line 89', 'redis-cluster,config', 0),
('cache-service', 'WARN-12001', 'Cache memory usage approaching critical threshold', 'HIGH', 'at memory.check() line 67', 'redis-cluster,monitoring', 0),
('cache-service', 'ERR-14003', 'Cache replication lag between cluster nodes', 'MEDIUM', 'at replication.check_lag() line 345\nat cache.sync() line 234', 'redis-cluster,replication', 0),
('cache-service', 'ERR-14004', 'Cache backup restoration failed after node recovery', 'MEDIUM', 'at backup.restore() line 123\nat cache.recover() line 167', 'backup-service,redis-cluster', 0);

-- Database Service Issues
INSERT INTO error_logs (service_name, error_code, error_message, severity, stack_trace, affected_components, user_impact) VALUES
('database-service', 'ERR-15001', 'MySQL master-slave replication lag detected', 'CRITICAL', 'at replication.check_lag() line 234\nat database.monitor() line 123', 'mysql-cluster,replication', 0),
('database-service', 'ERR-15002', 'Database connection pool exhaustion during peak load', 'CRITICAL', 'at pool.get_connection() line 345\nat database.query() line 167', 'mysql-cluster,connection-pool', 0),
('database-service', 'WARN-13001', 'Slow query log threshold exceeded for multiple queries', 'HIGH', 'at query.monitor() line 89', 'mysql-cluster,monitoring', 0),
('database-service', 'ERR-15003', 'Database backup job failed due to storage insufficient', 'HIGH', 'at backup.execute() line 156\nat database.backup() line 234', 'backup-service,storage', 0),
('database-service', 'ERR-15004', 'Database schema migration script execution failed', 'CRITICAL', 'at migration.execute() line 345\nat database.migrate() line 123', 'migration-service,mysql-cluster', 0),
('database-service', 'ERR-15005', 'Database index corruption detected on table scan', 'HIGH', 'at index.validate() line 67\nat database.check_integrity() line 89', 'mysql-cluster,maintenance', 0);

-- CDN Service Issues
INSERT INTO error_logs (service_name, error_code, error_message, severity, stack_trace, affected_components, user_impact) VALUES
('cdn-service', 'ERR-16001', 'CDN origin server health check failed', 'HIGH', 'at origin.health_check() line 234\nat cdn.monitor() line 123', 'origin-server,monitoring', 2000),
('cdn-service', 'ERR-16002', 'Cloudflare API rate limit exceeded for cache invalidation', 'MEDIUM', 'at cloudflare.invalidate() line 156\nat cdn.purge_cache() line 89', 'cloudflare-provider,api', 0),
('cdn-service', 'WARN-14001', 'CDN cache hit ratio below expected threshold', 'LOW', 'at cache.monitor_ratio() line 67', 'cdn,monitoring', 0),
('cdn-service', 'ERR-16003', 'SSL certificate renewal failed for CDN domains', 'HIGH', 'at ssl.renew() line 345\nat cdn.configure() line 167', 'ssl-service,cloudflare-provider', 0);

-- Workflow Service Issues
INSERT INTO error_logs (service_name, error_code, error_message, severity, stack_trace, affected_components, user_impact) VALUES
('workflow-service', 'ERR-17001', 'Task scheduler failed to trigger workflow execution', 'HIGH', 'at scheduler.trigger() line 234\nat workflow.execute() line 123', 'task-scheduler,database', 0),
('workflow-service', 'ERR-17002', 'Workflow step execution timeout in long-running process', 'MEDIUM', 'at step.execute() line 345\nat workflow.process() line 167', 'worker,timeout-handler', 0),
('workflow-service', 'WARN-15001', 'Workflow state persistence sync delay detected', 'LOW', 'at state.sync() line 89', 'database,cache', 0),
('workflow-service', 'ERR-17003', 'Workflow approval notification delivery failed', 'MEDIUM', 'at notification.send_approval() line 156\nat workflow.request_approval() line 234', 'notification-service,message-queue', 0);

-- Integration Service Issues
INSERT INTO error_logs (service_name, error_code, error_message, severity, stack_trace, affected_components, user_impact) VALUES
('integration-service', 'ERR-18001', 'External API client authentication token expired', 'HIGH', 'at api.refresh_token() line 234\nat integration.authenticate() line 123', 'api-client,external-service', 0),
('integration-service', 'ERR-18002', 'Data transformation pipeline failed for complex mapping', 'MEDIUM', 'at transform.execute() line 345\nat integration.process() line 167', 'transform-service,worker', 0),
('integration-service', 'WARN-16001', 'Integration retry queue backlog increasing', 'LOW', 'at retry.check_backlog() line 89', 'message-queue,worker', 0),
('integration-service', 'ERR-18003', 'Webhook signature validation failed for incoming requests', 'HIGH', 'at webhook.validate_signature() line 156\nat integration.receive() line 234', 'security,validation', 0),
('integration-service', 'ERR-18004', 'Bulk data sync job failed due to API rate limiting', 'MEDIUM', 'at sync.execute_bulk() line 67\nat integration.sync() line 123', 'external-api,rate-limiter', 0);

-- Insert Sample Incidents (Extended and Complex)
INSERT INTO incidents (incident_id, service_name, title, description, severity, status, affected_users, business_impact, assigned_to, incident_type, root_cause_category, resolution_notes, mitigation_steps) VALUES
('INC-2024-001', 'payment-service', 'Payment Processing Outage', 'Database connection timeout causing payment failures during peak hours', 'CRITICAL', 'OPEN', 1500, 'Revenue loss estimated at $50K/hour', 'payments-team', 'OUTAGE', 'NETWORK', NULL, 'Implementing database connection pooling and retry logic'),
('INC-2024-002', 'user-service', 'Authentication Service Degradation', 'LDAP connection timeout causing login delays for users', 'HIGH', 'IN_PROGRESS', 5000, 'User experience degradation, potential churn impact', 'identity-team', 'DEGRADATION', 'NETWORK', 'Implementing LDAP connection fallback', 'Added caching for user authentication data'),
('INC-2024-003', 'notification-service', 'Email Delivery Failures', 'Email provider API authentication failed preventing notifications', 'HIGH', 'OPEN', 200, 'Communication delays for time-sensitive notifications', 'communications-team', 'OUTAGE', 'EXTERNAL', NULL, 'Switching to backup email provider'),
('INC-2024-004', 'order-service', 'Order Creation Failures', 'Inventory service unavailable preventing new orders', 'CRITICAL', 'OPEN', 3500, 'Direct revenue impact, order fulfillment delays', 'ecommerce-team', 'OUTAGE', 'SOFTWARE', NULL, 'Implementing inventory service circuit breaker'),
('INC-2024-005', 'file-upload-service', 'File Upload System Outage', 'S3 upload connection timeout preventing file uploads', 'CRITICAL', 'OPEN', 4000, 'User functionality unavailable, content creation blocked', 'storage-team', 'OUTAGE', 'NETWORK', NULL, 'Implementing S3 upload retry with exponential backoff'),
('INC-2024-006', 'auth-service', 'OAuth Authentication Failure', 'OAuth provider token endpoint unavailable', 'CRITICAL', 'IN_PROGRESS', 6000, 'Complete authentication failure for OAuth users', 'security-team', 'OUTAGE', 'EXTERNAL', 'Implementing OAuth token caching', 'Added fallback authentication mechanism'),
('INC-2024-007', 'search-service', 'Search Service Degradation', 'Elasticsearch cluster health causing slow search results', 'HIGH', 'OPEN', 2000, 'User experience impact, discovery functionality affected', 'discovery-team', 'DEGRADATION', 'HARDWARE', NULL, 'Adding Elasticsearch cluster nodes'),
('INC-2024-008', 'order-service', 'Payment Callback Processing Issues', 'Payment callback handling failed causing order status sync issues', 'HIGH', 'OPEN', 900, 'Order status inconsistencies, payment reconciliation issues', 'ecommerce-team', 'DATA_LOSS', 'SOFTWARE', NULL, 'Implementing payment callback queue with retry'),
('INC-2024-009', 'api-gateway', 'API Gateway Circuit Breaker Activation', 'Circuit breaker triggered for multiple backend services causing request failures', 'CRITICAL', 'OPEN', 8000, 'Complete API unavailability for dependent services', 'platform-team', 'OUTAGE', 'SOFTWARE', NULL, 'Adjusting circuit breaker thresholds and timeouts'),
('INC-2024-010', 'database-service', 'Database Replication Lag Critical', 'MySQL master-slave replication lag exceeding 5 minutes causing data inconsistency', 'CRITICAL', 'IN_PROGRESS', 0, 'Data integrity risk, read/write inconsistency across services', 'database-team', 'DATA_LOSS', 'HARDWARE', 'Implementing read replica promotion', 'Added monitoring for replication lag'),
('INC-2024-011', 'cache-service', 'Redis Cluster Node Failure', 'Multiple Redis cluster nodes failed causing cache unavailability', 'HIGH', 'OPEN', 0, 'Performance degradation across all services, increased database load', 'infrastructure-team', 'OUTAGE', 'HARDWARE', NULL, 'Implementing Redis cluster auto-recovery'),
('INC-2024-012', 'recommendation-service', 'ML Model API Outage', 'External ML model API timeout preventing recommendation generation', 'MEDIUM', 'OPEN', 0, 'Personalization features unavailable, user engagement impact', 'ml-team', 'OUTAGE', 'EXTERNAL', NULL, 'Implementing local ML model fallback'),
('INC-2024-013', 'integration-service', 'External API Rate Limiting', 'Multiple external APIs rate limiting causing integration failures', 'HIGH', 'OPEN', 0, 'Third-party service integrations failing, business process disruption', 'integrations-team', 'DEGRADATION', 'EXTERNAL', NULL, 'Implementing API rate limiting and queuing'),
('INC-2024-014', 'workflow-service', 'Workflow Execution Queue Backlog', 'Task scheduler failures causing workflow execution delays', 'MEDIUM', 'OPEN', 0, 'Business process automation delays, operational efficiency impact', 'operations-team', 'PERFORMANCE', 'SOFTWARE', NULL, 'Implementing workflow priority queue'),
('INC-2024-015', 'cdn-service', 'CDN Origin Server Health Issues', 'Origin server health check failures causing CDN serving problems', 'HIGH', 'OPEN', 2000, 'Content delivery performance degradation, user experience impact', 'infrastructure-team', 'DEGRADATION', 'NETWORK', NULL, 'Implementing CDN origin server failover'),
('INC-2024-016', 'payment-service', 'Fraud Detection Service Timeout', 'Fraud detection service timeout during high-risk transaction processing', 'HIGH', 'OPEN', 450, 'Security risk, fraudulent transactions may be processed', 'payments-team', 'SECURITY', 'PERFORMANCE', NULL, 'Implementing fraud detection service scaling'),
('INC-2024-017', 'user-service', 'Multi-factor Authentication Issues', 'MFA service performance degradation causing authentication delays', 'MEDIUM', 'OPEN', 1000, 'Security feature impact, user experience degradation', 'security-team', 'DEGRADATION', 'PERFORMANCE', NULL, 'Implementing MFA service load balancing'),
('INC-2024-018', 'reporting-service', 'Report Generation Service Outage', 'Report export service timeout preventing business intelligence reports', 'MEDIUM', 'OPEN', 0, 'Business intelligence unavailable, decision-making impact', 'bi-team', 'OUTAGE', 'SOFTWARE', NULL, 'Implementing report generation queue system'),
('INC-2024-019', 'search-service', 'Search Index Rebuild Failure', 'Search index rebuild failed causing stale search results', 'HIGH', 'OPEN', 3000, 'User experience impact, discovery functionality outdated', 'discovery-team', 'DATA_LOSS', 'SOFTWARE', NULL, 'Implementing incremental index updates'),
('INC-2024-020', 'auth-service', 'Single Sign-On Integration Failure', 'SSO integration timeout preventing enterprise authentication', 'CRITICAL', 'OPEN', 3500, 'Enterprise users unable to authenticate, business disruption', 'security-team', 'OUTAGE', 'EXTERNAL', NULL, 'Implementing SSO provider failover');

-- Create Indexes for better query performance
CREATE INDEX idx_error_logs_service ON error_logs(service_name);
CREATE INDEX idx_error_logs_severity ON error_logs(severity);
CREATE INDEX idx_error_logs_timestamp ON error_logs(timestamp);
CREATE INDEX idx_incidents_service ON incidents(service_name);
CREATE INDEX idx_incidents_severity ON incidents(severity);
CREATE INDEX idx_incidents_status ON incidents(status);

-- Display summary
SELECT 'Database setup completed!' AS Status;
SELECT COUNT(*) AS total_services FROM services;
SELECT COUNT(*) AS total_error_logs FROM error_logs;
SELECT COUNT(*) AS total_incidents FROM incidents;

-- Additional summary queries
SELECT service_name, COUNT(*) as error_count 
FROM error_logs 
GROUP BY service_name 
ORDER BY error_count DESC;

SELECT severity, COUNT(*) as incident_count 
FROM incidents 
GROUP BY severity 
ORDER BY incident_count DESC;

SELECT incident_type, COUNT(*) as type_count 
FROM incidents 
GROUP BY incident_type 
ORDER BY type_count DESC;