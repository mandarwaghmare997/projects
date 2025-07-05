"""
Monitoring API Routes for Qryti Learn
Provides system health and performance metrics
"""

from flask import Blueprint, jsonify, request
from ..utils.performance_monitor import performance_monitor
from datetime import datetime
import os

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'service': 'qryti-learn-api',
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@monitoring_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get comprehensive system metrics"""
    try:
        metrics = {
            'system': performance_monitor.get_system_metrics(),
            'api': performance_monitor.get_api_metrics(),
            'health': performance_monitor.get_health_status(),
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/metrics/endpoints', methods=['GET'])
def get_endpoint_metrics():
    """Get performance metrics by endpoint"""
    try:
        endpoint_stats = performance_monitor.get_endpoint_stats()
        return jsonify({
            'endpoints': endpoint_stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/metrics/export', methods=['POST'])
def export_metrics():
    """Export metrics to file"""
    try:
        filepath = f"/tmp/qryti_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        performance_monitor.export_metrics(filepath)
        return jsonify({
            'message': 'Metrics exported successfully',
            'filepath': filepath,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/status', methods=['GET'])
def get_status():
    """Get detailed system status"""
    try:
        system_metrics = performance_monitor.get_system_metrics()
        api_metrics = performance_monitor.get_api_metrics()
        health_status = performance_monitor.get_health_status()
        
        return jsonify({
            'service_info': {
                'name': 'Qryti Learn API',
                'version': '1.0.0',
                'environment': os.getenv('FLASK_ENV', 'development'),
                'uptime_hours': system_metrics['uptime_hours']
            },
            'system_health': {
                'status': health_status['status'],
                'score': health_status['health_score'],
                'issues': health_status['issues']
            },
            'performance': {
                'cpu_usage': system_metrics['cpu_percent'],
                'memory_usage': system_metrics['memory_percent'],
                'disk_usage': system_metrics['disk_usage'],
                'avg_response_time': api_metrics['average_response_time'],
                'requests_per_minute': api_metrics['requests_per_minute'],
                'error_rate': api_metrics['error_rate']
            },
            'api_stats': {
                'total_requests': api_metrics['total_requests'],
                'slow_queries': api_metrics['slow_queries_count']
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get system alerts and warnings"""
    try:
        system_metrics = performance_monitor.get_system_metrics()
        api_metrics = performance_monitor.get_api_metrics()
        
        alerts = []
        
        # System alerts
        if system_metrics['cpu_percent'] > 80:
            alerts.append({
                'type': 'warning',
                'category': 'system',
                'message': f"High CPU usage: {system_metrics['cpu_percent']:.1f}%",
                'severity': 'high' if system_metrics['cpu_percent'] > 90 else 'medium'
            })
        
        if system_metrics['memory_percent'] > 85:
            alerts.append({
                'type': 'warning',
                'category': 'system',
                'message': f"High memory usage: {system_metrics['memory_percent']:.1f}%",
                'severity': 'high' if system_metrics['memory_percent'] > 95 else 'medium'
            })
        
        if system_metrics['disk_usage'] > 90:
            alerts.append({
                'type': 'warning',
                'category': 'system',
                'message': f"High disk usage: {system_metrics['disk_usage']:.1f}%",
                'severity': 'high'
            })
        
        # API alerts
        if api_metrics['average_response_time'] > 1000:
            alerts.append({
                'type': 'warning',
                'category': 'performance',
                'message': f"Slow API responses: {api_metrics['average_response_time']:.1f}ms average",
                'severity': 'medium'
            })
        
        if api_metrics['error_rate'] > 5:
            alerts.append({
                'type': 'error',
                'category': 'api',
                'message': f"High error rate: {api_metrics['error_rate']:.1f}%",
                'severity': 'high' if api_metrics['error_rate'] > 10 else 'medium'
            })
        
        if api_metrics['slow_queries_count'] > 10:
            alerts.append({
                'type': 'warning',
                'category': 'performance',
                'message': f"Multiple slow queries detected: {api_metrics['slow_queries_count']}",
                'severity': 'medium'
            })
        
        return jsonify({
            'alerts': alerts,
            'alert_count': len(alerts),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

