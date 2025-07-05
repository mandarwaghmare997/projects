"""
Performance Monitoring Utility for Qryti Learn
Tracks API performance, database queries, and system metrics
"""

import time
import psutil
import logging
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

class PerformanceMonitor:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.request_times = deque(maxlen=1000)  # Keep last 1000 requests
        self.slow_queries = deque(maxlen=100)    # Keep last 100 slow queries
        self.error_count = defaultdict(int)
        self.start_time = datetime.now()
        
    def track_request(self, endpoint, method, duration, status_code):
        """Track API request performance"""
        self.request_times.append({
            'endpoint': endpoint,
            'method': method,
            'duration': duration,
            'status_code': status_code,
            'timestamp': datetime.now().isoformat()
        })
        
        # Track slow requests (>1 second)
        if duration > 1000:
            self.slow_queries.append({
                'endpoint': endpoint,
                'method': method,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
    
    def track_error(self, error_type, endpoint=None):
        """Track application errors"""
        key = f"{error_type}:{endpoint}" if endpoint else error_type
        self.error_count[key] += 1
    
    def get_system_metrics(self):
        """Get current system performance metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600
        }
    
    def get_api_metrics(self):
        """Get API performance metrics"""
        if not self.request_times:
            return {
                'total_requests': 0,
                'average_response_time': 0,
                'requests_per_minute': 0,
                'error_rate': 0
            }
        
        # Calculate metrics from recent requests
        recent_requests = [r for r in self.request_times 
                          if datetime.fromisoformat(r['timestamp']) > datetime.now() - timedelta(minutes=5)]
        
        total_requests = len(self.request_times)
        avg_response_time = sum(r['duration'] for r in self.request_times) / total_requests
        requests_per_minute = len(recent_requests)
        
        error_requests = [r for r in self.request_times if r['status_code'] >= 400]
        error_rate = (len(error_requests) / total_requests) * 100 if total_requests > 0 else 0
        
        return {
            'total_requests': total_requests,
            'average_response_time': round(avg_response_time, 2),
            'requests_per_minute': requests_per_minute,
            'error_rate': round(error_rate, 2),
            'slow_queries_count': len(self.slow_queries)
        }
    
    def get_endpoint_stats(self):
        """Get performance stats by endpoint"""
        endpoint_stats = defaultdict(lambda: {'count': 0, 'total_time': 0, 'errors': 0})
        
        for request in self.request_times:
            endpoint = request['endpoint']
            endpoint_stats[endpoint]['count'] += 1
            endpoint_stats[endpoint]['total_time'] += request['duration']
            if request['status_code'] >= 400:
                endpoint_stats[endpoint]['errors'] += 1
        
        # Calculate averages
        for endpoint, stats in endpoint_stats.items():
            stats['average_time'] = round(stats['total_time'] / stats['count'], 2)
            stats['error_rate'] = round((stats['errors'] / stats['count']) * 100, 2)
        
        return dict(endpoint_stats)
    
    def get_health_status(self):
        """Get overall system health status"""
        system_metrics = self.get_system_metrics()
        api_metrics = self.get_api_metrics()
        
        # Determine health status based on metrics
        health_score = 100
        issues = []
        
        if system_metrics['cpu_percent'] > 80:
            health_score -= 20
            issues.append("High CPU usage")
        
        if system_metrics['memory_percent'] > 85:
            health_score -= 20
            issues.append("High memory usage")
        
        if api_metrics['average_response_time'] > 1000:
            health_score -= 15
            issues.append("Slow API responses")
        
        if api_metrics['error_rate'] > 5:
            health_score -= 25
            issues.append("High error rate")
        
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 70:
            status = "good"
        elif health_score >= 50:
            status = "warning"
        else:
            status = "critical"
        
        return {
            'status': status,
            'health_score': max(0, health_score),
            'issues': issues,
            'timestamp': datetime.now().isoformat()
        }
    
    def export_metrics(self, filepath):
        """Export metrics to JSON file for analysis"""
        metrics_data = {
            'system_metrics': self.get_system_metrics(),
            'api_metrics': self.get_api_metrics(),
            'endpoint_stats': self.get_endpoint_stats(),
            'health_status': self.get_health_status(),
            'recent_requests': list(self.request_times)[-100:],  # Last 100 requests
            'slow_queries': list(self.slow_queries),
            'error_summary': dict(self.error_count),
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2)

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            performance_monitor.track_error(type(e).__name__, func.__name__)
            raise
        finally:
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds
            performance_monitor.track_request(
                endpoint=func.__name__,
                method='FUNCTION',
                duration=duration,
                status_code=200
            )
    return wrapper

def monitor_api_request(func):
    """Decorator to monitor API request performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request, g
        
        start_time = time.time()
        g.start_time = start_time
        
        try:
            result = func(*args, **kwargs)
            status_code = getattr(result, 'status_code', 200)
            return result
        except Exception as e:
            performance_monitor.track_error(type(e).__name__, request.endpoint)
            status_code = 500
            raise
        finally:
            duration = (time.time() - start_time) * 1000
            performance_monitor.track_request(
                endpoint=request.endpoint or 'unknown',
                method=request.method,
                duration=duration,
                status_code=status_code
            )
    return wrapper

