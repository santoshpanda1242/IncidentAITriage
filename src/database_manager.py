import mysql.connector
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class MySQLDatabase:
    """MySQL database connection for incident logs"""
    
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD', ''),
                database=os.getenv('MYSQL_DATABASE', 'incident_logs')
            )
            print("✓ MySQL connection established successfully")
        except mysql.connector.Error as err:
            print(f"✗ MySQL connection error: {err}")
            print("✗ Please check your MySQL configuration in .env file")
            # For development, continue without connection
            self.connection = None
    
    def get_error_logs(self, service_name: str, time_range_hours: int = 24) -> List[Dict[str, Any]]:
        """Query error logs for a specific service"""
        if not self.connection:
            print("✗ No database connection - using mock data")
            return self._get_mock_error_logs(service_name)
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            # First try without time constraint to see if data exists
            query = """
            SELECT * FROM error_logs 
            WHERE service_name = %s 
            ORDER BY timestamp DESC
            """
            cursor.execute(query, (service_name,))
            logs = cursor.fetchall()
            cursor.close()
            print(f"✓ Retrieved {len(logs)} error logs from MySQL for {service_name}")
            return logs
        except mysql.connector.Error as err:
            print(f"✗ Query error: {err}")
            print("✗ Falling back to mock data")
            return self._get_mock_error_logs(service_name)
    
    def _get_mock_error_logs(self, service_name: str) -> List[Dict[str, Any]]:
        """Mock error logs for development/testing fallback"""
        base_time = datetime.now()
        return [
            {
                'log_id': 1,
                'service_name': service_name,
                'error_code': 'ERR-5001',
                'error_message': 'Database connection timeout during payment processing',
                'severity': 'CRITICAL',
                'timestamp': base_time,
                'stack_trace': 'at db.connect() line 45\nat payment.process() line 120',
                'affected_components': 'database,payment-gateway',
                'user_impact': 1500,
                'resolution_status': 'OPEN'
            },
            {
                'log_id': 2,
                'service_name': service_name,
                'error_code': 'ERR-5002',
                'error_message': 'Payment gateway API rate limit exceeded',
                'severity': 'HIGH',
                'timestamp': base_time,
                'stack_trace': 'at gateway.request() line 78\nat payment.process() line 130',
                'affected_components': 'payment-gateway,api',
                'user_impact': 800,
                'resolution_status': 'OPEN'
            },
            {
                'log_id': 3,
                'service_name': service_name,
                'error_code': 'WARN-1001',
                'error_message': 'High memory usage in payment processing',
                'severity': 'MEDIUM',
                'timestamp': base_time,
                'stack_trace': 'at memory.check() line 45',
                'affected_components': 'cache,payment-worker',
                'user_impact': 0,
                'resolution_status': 'OPEN'
            }
        ]
    
    def get_incident_data(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get incident details by ID"""
        if not self.connection:
            print("✗ No database connection - using mock incident data")
            return self._get_mock_incident(incident_id)
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM incidents WHERE incident_id = %s"
            cursor.execute(query, (incident_id,))
            incident = cursor.fetchone()
            cursor.close()
            if incident:
                print(f"✓ Retrieved incident {incident_id} from MySQL")
            else:
                print(f"✗ Incident {incident_id} not found in MySQL, using mock data")
                return self._get_mock_incident(incident_id)
            return incident
        except mysql.connector.Error as err:
            print(f"✗ Query error: {err}")
            print("✗ Falling back to mock incident data")
            return self._get_mock_incident(incident_id)
    
    def _get_mock_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Mock incident data for development/testing fallback"""
        incidents = {
            'INC-2024-001': {
                'incident_id': 'INC-2024-001',
                'service_name': 'payment-service',
                'title': 'Payment Processing Outage',
                'description': 'Database connection timeout causing payment failures during peak hours',
                'severity': 'CRITICAL',
                'status': 'OPEN',
                'affected_users': 1500,
                'business_impact': 'Revenue loss estimated at $50K/hour',
                'assigned_to': 'payments-team',
                'incident_type': 'OUTAGE',
                'root_cause_category': 'NETWORK',
                'resolution_notes': None,
                'mitigation_steps': 'Implementing database connection pooling and retry logic'
            },
            'INC-2024-002': {
                'incident_id': 'INC-2024-002',
                'service_name': 'user-service',
                'title': 'Authentication Service Degradation',
                'description': 'LDAP connection timeout causing login delays for users',
                'severity': 'HIGH',
                'status': 'IN_PROGRESS',
                'affected_users': 5000,
                'business_impact': 'User experience degradation, potential churn impact',
                'assigned_to': 'identity-team',
                'incident_type': 'DEGRADATION',
                'root_cause_category': 'NETWORK',
                'resolution_notes': 'Implementing LDAP connection fallback',
                'mitigation_steps': 'Added caching for user authentication data'
            }
        }
        return incidents.get(incident_id)
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()


class MongoProfileMock:
    """Mock MongoDB connection for service profiles"""
    
    def __init__(self):
        # Mock data store
        self.service_profiles = {
            'payment-service': {
                'service_id': 'svc-001',
                'name': 'payment-service',
                'version': '2.3.1',
                'environment': 'production',
                'team': 'payments',
                'criticality': 'HIGH',
                'dependencies': ['database', 'cache', 'api-gateway', 'payment-gateway', 'fraud-detection'],
                'sla_target': '99.9%'
            },
            'user-service': {
                'service_id': 'svc-002',
                'name': 'user-service',
                'version': '1.8.4',
                'environment': 'production',
                'team': 'identity',
                'criticality': 'MEDIUM',
                'dependencies': ['database', 'auth-service', 'ldap', 'session-store'],
                'sla_target': '99.5%'
            },
            'order-service': {
                'service_id': 'svc-004',
                'name': 'order-service',
                'version': '4.2.0',
                'environment': 'production',
                'team': 'ecommerce',
                'criticality': 'HIGH',
                'dependencies': ['database', 'inventory-service', 'payment-service', 'shipping-service'],
                'sla_target': '99.9%'
            }
        }
    
    def get_service_profile(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get service profile by name"""
        return self.service_profiles.get(service_name)
    
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all service profiles"""
        return list(self.service_profiles.values())


class DatabaseManager:
    """Manager for all database connections"""
    
    def __init__(self):
        self.mysql_db = MySQLDatabase()
        self.mongo_mock = MongoProfileMock()
    
    def get_incident_context(self, service_name: str, incident_id: str = None) -> Dict[str, Any]:
        """Get complete incident context from all sources"""
        error_logs = self.mysql_db.get_error_logs(service_name)
        service_profile = self.mongo_mock.get_service_profile(service_name)
        incident_data = None
        
        if incident_id:
            incident_data = self.mysql_db.get_incident_data(incident_id)
        
        return {
            'service_name': service_name,
            'incident_id': incident_id,
            'incident_data': incident_data,
            'error_logs': error_logs,
            'service_profile': service_profile,
            'query_timestamp': datetime.now().isoformat()
        }
    
    def close(self):
        """Close all database connections"""
        self.mysql_db.close()


# Sample incident scenarios for testing
SAMPLE_INCIDENTS = [
    {
        'incident_id': 'INC-2024-001',
        'service_name': 'payment-service',
        'description': 'Payment processing failures during peak hours',
        'severity': 'CRITICAL',
        'affected_users': 1500,
        'business_impact': 'Revenue loss estimated at $50K/hour'
    },
    {
        'incident_id': 'INC-2024-002',
        'service_name': 'user-service',
        'description': 'User authentication delays',
        'severity': 'HIGH',
        'affected_users': 5000,
        'business_impact': 'User experience degradation, potential churn'
    },
    {
        'incident_id': 'INC-2024-004',
        'service_name': 'order-service',
        'description': 'Order creation failures due to inventory issues',
        'severity': 'CRITICAL',
        'affected_users': 3500,
        'business_impact': 'Direct revenue impact, order fulfillment delays'
    }
]