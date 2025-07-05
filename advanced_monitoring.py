#!/usr/bin/env python3
"""
Advanced Monitoring System for Qryti Learn
Comprehensive system monitoring, alerting, and performance tracking
"""

import psutil
import sqlite3
import requests
import json
import time
import logging
from datetime import datetime, timedelta
import os
import threading
from collections import defaultdict, deque

class QrytiLearnMonitor:
    def __init__(self, config_file="monitoring_config.json"):
        self.config = self.load_config(config_file)
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.alerts = []
        self.setup_logging()
        
    def load_config(self, config_file):
        """Load monitoring configuration"""
        default_config = {
            "api_base_url": "http://localhost:5002",
            "database_path": "/home/ubuntu/projects/backend/src/database/app.db",
            "monitoring_interval": 60,  # seconds
            "alert_thresholds": {
                "cpu_usage": 80,
                "memory_usage": 85,
                "disk_usage": 90,
                "api_response_time": 1000,  # ms
                "error_rate": 5  # percentage
            },
            "health_check_endpoints": [
                "/api/health",
                "/api/courses",
                "/api/quizzes",
                "/api/certificates/stats",
                "/api/knowledge/stats"
            ]
        }
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except FileNotFoundError:
            return default_config
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/home/ubuntu/projects/monitoring.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_system_metrics(self):
        """Collect system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'usage_percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'usage_percent': disk.percent
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }
            
            # Store metrics history
            self.metrics_history['system'].append(metrics)
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return None
    
    def check_database_health(self):
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            conn = sqlite3.connect(self.config['database_path'])
            cursor = conn.cursor()
            
            # Test basic connectivity
            cursor.execute("SELECT 1")
            cursor.fetchone()
            
            # Get database size
            db_size = os.path.getsize(self.config['database_path'])
            
            # Count total records across main tables
            tables = ['users', 'courses', 'quizzes', 'certificates', 'knowledge_resources']
            table_counts = {}
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_counts[table] = count
                except sqlite3.OperationalError:
                    table_counts[table] = 0
            
            conn.close()
            response_time = (time.time() - start_time) * 1000  # ms
            
            db_metrics = {
                'timestamp': datetime.now().isoformat(),
                'status': 'healthy',
                'response_time_ms': response_time,
                'database_size_bytes': db_size,
                'table_counts': table_counts,
                'total_records': sum(table_counts.values())
            }
            
            self.metrics_history['database'].append(db_metrics)
            return db_metrics
            
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_api_health(self):
        """Check API endpoint health and performance"""
        api_metrics = {
            'timestamp': datetime.now().isoformat(),
            'endpoints': {},
            'overall_status': 'healthy',
            'total_response_time': 0,
            'successful_endpoints': 0,
            'failed_endpoints': 0
        }
        
        for endpoint in self.config['health_check_endpoints']:
            try:
                start_time = time.time()
                url = f"{self.config['api_base_url']}{endpoint}"
                
                response = requests.get(url, timeout=10)
                response_time = (time.time() - start_time) * 1000  # ms
                
                endpoint_data = {
                    'status_code': response.status_code,
                    'response_time_ms': response_time,
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'content_length': len(response.content) if response.content else 0
                }
                
                if response.status_code == 200:
                    api_metrics['successful_endpoints'] += 1
                    api_metrics['total_response_time'] += response_time
                else:
                    api_metrics['failed_endpoints'] += 1
                    api_metrics['overall_status'] = 'degraded'
                
                api_metrics['endpoints'][endpoint] = endpoint_data
                
            except Exception as e:
                self.logger.error(f"API health check failed for {endpoint}: {e}")
                api_metrics['endpoints'][endpoint] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'response_time_ms': None
                }
                api_metrics['failed_endpoints'] += 1
                api_metrics['overall_status'] = 'unhealthy'
        
        # Calculate average response time
        if api_metrics['successful_endpoints'] > 0:
            api_metrics['average_response_time'] = api_metrics['total_response_time'] / api_metrics['successful_endpoints']
        else:
            api_metrics['average_response_time'] = None
        
        self.metrics_history['api'].append(api_metrics)
        return api_metrics
    
    def check_alert_conditions(self, system_metrics, db_metrics, api_metrics):
        """Check for alert conditions and generate alerts"""
        alerts = []
        thresholds = self.config['alert_thresholds']
        
        # System resource alerts
        if system_metrics:
            if system_metrics['cpu']['usage_percent'] > thresholds['cpu_usage']:
                alerts.append({
                    'type': 'system',
                    'severity': 'warning',
                    'message': f"High CPU usage: {system_metrics['cpu']['usage_percent']:.1f}%",
                    'timestamp': datetime.now().isoformat()
                })
            
            if system_metrics['memory']['usage_percent'] > thresholds['memory_usage']:
                alerts.append({
                    'type': 'system',
                    'severity': 'warning',
                    'message': f"High memory usage: {system_metrics['memory']['usage_percent']:.1f}%",
                    'timestamp': datetime.now().isoformat()
                })
            
            if system_metrics['disk']['usage_percent'] > thresholds['disk_usage']:
                alerts.append({
                    'type': 'system',
                    'severity': 'critical',
                    'message': f"High disk usage: {system_metrics['disk']['usage_percent']:.1f}%",
                    'timestamp': datetime.now().isoformat()
                })
        
        # Database alerts
        if db_metrics and db_metrics['status'] != 'healthy':
            alerts.append({
                'type': 'database',
                'severity': 'critical',
                'message': f"Database unhealthy: {db_metrics.get('error', 'Unknown error')}",
                'timestamp': datetime.now().isoformat()
            })
        
        # API alerts
        if api_metrics:
            if api_metrics['overall_status'] == 'unhealthy':
                alerts.append({
                    'type': 'api',
                    'severity': 'critical',
                    'message': f"API unhealthy: {api_metrics['failed_endpoints']} endpoints failed",
                    'timestamp': datetime.now().isoformat()
                })
            elif api_metrics['overall_status'] == 'degraded':
                alerts.append({
                    'type': 'api',
                    'severity': 'warning',
                    'message': f"API degraded: {api_metrics['failed_endpoints']} endpoints failed",
                    'timestamp': datetime.now().isoformat()
                })
            
            if api_metrics['average_response_time'] and api_metrics['average_response_time'] > thresholds['api_response_time']:
                alerts.append({
                    'type': 'api',
                    'severity': 'warning',
                    'message': f"High API response time: {api_metrics['average_response_time']:.1f}ms",
                    'timestamp': datetime.now().isoformat()
                })
        
        # Store alerts
        self.alerts.extend(alerts)
        
        # Log alerts
        for alert in alerts:
            self.logger.warning(f"ALERT [{alert['severity'].upper()}] {alert['type']}: {alert['message']}")
        
        return alerts
    
    def generate_health_report(self):
        """Generate comprehensive health report"""
        system_metrics = self.get_system_metrics()
        db_metrics = self.check_database_health()
        api_metrics = self.check_api_health()
        alerts = self.check_alert_conditions(system_metrics, db_metrics, api_metrics)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': self.determine_overall_status(system_metrics, db_metrics, api_metrics),
            'system': system_metrics,
            'database': db_metrics,
            'api': api_metrics,
            'alerts': alerts,
            'metrics_summary': self.get_metrics_summary()
        }
        
        return report
    
    def determine_overall_status(self, system_metrics, db_metrics, api_metrics):
        """Determine overall system status"""
        if not system_metrics or not db_metrics or not api_metrics:
            return 'unknown'
        
        # Check for critical conditions
        if (db_metrics['status'] == 'unhealthy' or 
            api_metrics['overall_status'] == 'unhealthy' or
            (system_metrics and system_metrics['disk']['usage_percent'] > 95)):
            return 'critical'
        
        # Check for warning conditions
        if (api_metrics['overall_status'] == 'degraded' or
            (system_metrics and (
                system_metrics['cpu']['usage_percent'] > 80 or
                system_metrics['memory']['usage_percent'] > 85
            ))):
            return 'warning'
        
        return 'healthy'
    
    def get_metrics_summary(self):
        """Get summary of recent metrics"""
        summary = {}
        
        # System metrics summary
        if self.metrics_history['system']:
            recent_system = list(self.metrics_history['system'])[-10:]  # Last 10 readings
            summary['system'] = {
                'avg_cpu': sum(m['cpu']['usage_percent'] for m in recent_system) / len(recent_system),
                'avg_memory': sum(m['memory']['usage_percent'] for m in recent_system) / len(recent_system),
                'avg_disk': sum(m['disk']['usage_percent'] for m in recent_system) / len(recent_system)
            }
        
        # API metrics summary
        if self.metrics_history['api']:
            recent_api = list(self.metrics_history['api'])[-10:]
            successful_apis = [m for m in recent_api if m['average_response_time']]
            if successful_apis:
                summary['api'] = {
                    'avg_response_time': sum(m['average_response_time'] for m in successful_apis) / len(successful_apis),
                    'success_rate': sum(1 for m in recent_api if m['overall_status'] == 'healthy') / len(recent_api) * 100
                }
        
        # Database metrics summary
        if self.metrics_history['database']:
            recent_db = list(self.metrics_history['database'])[-10:]
            healthy_db = [m for m in recent_db if m['status'] == 'healthy']
            if healthy_db:
                summary['database'] = {
                    'avg_response_time': sum(m['response_time_ms'] for m in healthy_db) / len(healthy_db),
                    'uptime_percentage': len(healthy_db) / len(recent_db) * 100
                }
        
        return summary
    
    def save_report(self, report, filename=None):
        """Save health report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/home/ubuntu/projects/health_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            self.logger.info(f"Health report saved to {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Failed to save health report: {e}")
            return None
    
    def run_continuous_monitoring(self, duration_minutes=60):
        """Run continuous monitoring for specified duration"""
        self.logger.info(f"Starting continuous monitoring for {duration_minutes} minutes...")
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        interval = self.config['monitoring_interval']
        
        while datetime.now() < end_time:
            try:
                report = self.generate_health_report()
                
                # Print status update
                status = report['overall_status']
                print(f"[{datetime.now().strftime('%H:%M:%S')}] System Status: {status.upper()}")
                
                if report['alerts']:
                    print(f"  🚨 {len(report['alerts'])} active alerts")
                
                if report['system']:
                    sys = report['system']
                    print(f"  💻 CPU: {sys['cpu']['usage_percent']:.1f}% | Memory: {sys['memory']['usage_percent']:.1f}% | Disk: {sys['disk']['usage_percent']:.1f}%")
                
                if report['api'] and report['api']['average_response_time']:
                    print(f"  🌐 API: {report['api']['average_response_time']:.1f}ms avg | {report['api']['successful_endpoints']}/{len(report['api']['endpoints'])} endpoints healthy")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                self.logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error during monitoring cycle: {e}")
                time.sleep(interval)
        
        # Generate final report
        final_report = self.generate_health_report()
        report_file = self.save_report(final_report)
        
        self.logger.info("Continuous monitoring completed")
        return final_report, report_file

def main():
    """Main monitoring function"""
    print("🔍 Qryti Learn Advanced Monitoring System")
    print("=" * 50)
    
    monitor = QrytiLearnMonitor()
    
    # Generate immediate health report
    print("📊 Generating Health Report...")
    report = monitor.generate_health_report()
    
    # Display summary
    print(f"\n🎯 Overall Status: {report['overall_status'].upper()}")
    
    if report['system']:
        sys = report['system']
        print(f"💻 System: CPU {sys['cpu']['usage_percent']:.1f}% | Memory {sys['memory']['usage_percent']:.1f}% | Disk {sys['disk']['usage_percent']:.1f}%")
    
    if report['database']:
        db = report['database']
        print(f"🗄️  Database: {db['status']} | Response: {db.get('response_time_ms', 'N/A')}ms")
    
    if report['api']:
        api = report['api']
        print(f"🌐 API: {api['overall_status']} | Avg Response: {api.get('average_response_time', 'N/A')}ms")
    
    if report['alerts']:
        print(f"\n🚨 Active Alerts: {len(report['alerts'])}")
        for alert in report['alerts'][-5:]:  # Show last 5 alerts
            print(f"  [{alert['severity'].upper()}] {alert['message']}")
    
    # Save report
    report_file = monitor.save_report(report)
    print(f"\n📄 Full report saved to: {report_file}")
    
    return report

if __name__ == "__main__":
    main()

