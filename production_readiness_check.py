#!/usr/bin/env python3
"""
Production Readiness Check for Qryti Learn
Comprehensive validation of system readiness for production deployment
"""

import os
import json
import sqlite3
import requests
import subprocess
import time
from datetime import datetime
import psutil

class ProductionReadinessChecker:
    def __init__(self):
        self.checks = []
        self.critical_failures = []
        self.warnings = []
        self.base_url = "http://localhost:5002"
        self.project_dir = "/home/ubuntu/projects"
        
    def log_check(self, category, check_name, status, details=None, critical=False):
        """Log a readiness check result"""
        result = {
            'category': category,
            'check': check_name,
            'status': status,
            'details': details,
            'critical': critical,
            'timestamp': datetime.now().isoformat()
        }
        
        self.checks.append(result)
        
        if status == 'FAIL' and critical:
            self.critical_failures.append(result)
        elif status == 'WARN':
            self.warnings.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        critical_marker = " [CRITICAL]" if critical else ""
        print(f"{status_icon} {category}: {check_name}{critical_marker}")
        if details:
            print(f"   📝 {details}")
    
    def check_system_requirements(self):
        """Check system requirements for production deployment"""
        print("🖥️ Checking System Requirements...")
        
        # CPU check
        cpu_count = psutil.cpu_count()
        if cpu_count >= 2:
            self.log_check("System", "CPU Cores", "PASS", f"{cpu_count} cores available")
        else:
            self.log_check("System", "CPU Cores", "WARN", f"Only {cpu_count} cores (2+ recommended)")
        
        # Memory check
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        if memory_gb >= 4:
            self.log_check("System", "Memory", "PASS", f"{memory_gb:.1f}GB available")
        else:
            self.log_check("System", "Memory", "WARN", f"Only {memory_gb:.1f}GB (4GB+ recommended)")
        
        # Disk space check
        disk = psutil.disk_usage('/')
        disk_free_gb = disk.free / (1024**3)
        if disk_free_gb >= 10:
            self.log_check("System", "Disk Space", "PASS", f"{disk_free_gb:.1f}GB free")
        else:
            self.log_check("System", "Disk Space", "FAIL", f"Only {disk_free_gb:.1f}GB free (10GB+ required)", critical=True)
        
        # Python version check
        try:
            result = subprocess.run(['python3.11', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.log_check("System", "Python Version", "PASS", result.stdout.strip())
            else:
                self.log_check("System", "Python Version", "FAIL", "Python 3.11 not found", critical=True)
        except FileNotFoundError:
            self.log_check("System", "Python Version", "FAIL", "Python 3.11 not found", critical=True)
    
    def check_dependencies(self):
        """Check required dependencies and packages"""
        print("📦 Checking Dependencies...")
        
        # Check if backend requirements are installed
        requirements_file = os.path.join(self.project_dir, "backend", "requirements.txt")
        if os.path.exists(requirements_file):
            self.log_check("Dependencies", "Requirements File", "PASS", "requirements.txt found")
            
            # Try importing key packages
            key_packages = ['flask', 'sqlalchemy', 'jwt', 'reportlab', 'requests']
            for package in key_packages:
                try:
                    __import__(package)
                    self.log_check("Dependencies", f"Package {package}", "PASS", "Installed")
                except ImportError:
                    self.log_check("Dependencies", f"Package {package}", "FAIL", "Not installed", critical=True)
        else:
            self.log_check("Dependencies", "Requirements File", "FAIL", "requirements.txt not found", critical=True)
        
        # Check psutil for monitoring
        try:
            import psutil
            self.log_check("Dependencies", "Monitoring (psutil)", "PASS", "Available for system monitoring")
        except ImportError:
            self.log_check("Dependencies", "Monitoring (psutil)", "WARN", "Not available - install for monitoring")
    
    def check_database_integrity(self):
        """Check database structure and integrity"""
        print("🗄️ Checking Database Integrity...")
        
        db_path = os.path.join(self.project_dir, "backend", "src", "database", "app.db")
        
        if not os.path.exists(db_path):
            self.log_check("Database", "Database File", "FAIL", "Database file not found", critical=True)
            return
        
        self.log_check("Database", "Database File", "PASS", f"Found at {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check essential tables
            essential_tables = [
                'users', 'courses', 'modules', 'quizzes', 'questions',
                'certificates', 'knowledge_resources', 'videos'
            ]
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            for table in essential_tables:
                if table in existing_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    self.log_check("Database", f"Table {table}", "PASS", f"{count} records")
                else:
                    self.log_check("Database", f"Table {table}", "WARN", "Table missing")
            
            # Check database size
            db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
            self.log_check("Database", "Database Size", "PASS", f"{db_size_mb:.2f}MB")
            
            conn.close()
            
        except Exception as e:
            self.log_check("Database", "Database Connection", "FAIL", f"Error: {e}", critical=True)
    
    def check_api_endpoints(self):
        """Check API endpoint functionality"""
        print("🌐 Checking API Endpoints...")
        
        # Check if backend is running
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                self.log_check("API", "Health Endpoint", "PASS", "API server responding")
                
                # Test core endpoints
                endpoints = [
                    ("/api/courses", "Courses API"),
                    ("/api/quizzes", "Quizzes API"),
                    ("/api/certificates/stats", "Certificates API"),
                    ("/api/knowledge/stats", "Knowledge Base API")
                ]
                
                for endpoint, name in endpoints:
                    try:
                        resp = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                        if resp.status_code == 200:
                            self.log_check("API", name, "PASS", f"Status {resp.status_code}")
                        elif resp.status_code == 401:
                            self.log_check("API", name, "PASS", "Requires authentication (expected)")
                        else:
                            self.log_check("API", name, "WARN", f"Status {resp.status_code}")
                    except Exception as e:
                        self.log_check("API", name, "FAIL", f"Error: {e}")
                        
            else:
                self.log_check("API", "Health Endpoint", "FAIL", f"Status {response.status_code}", critical=True)
                
        except Exception as e:
            self.log_check("API", "API Server", "FAIL", f"Server not responding: {e}", critical=True)
    
    def check_security_configuration(self):
        """Check security configuration"""
        print("🔐 Checking Security Configuration...")
        
        # Check for environment variables
        security_vars = [
            'JWT_SECRET_KEY',
            'DATABASE_URL',
            'FLASK_ENV'
        ]
        
        for var in security_vars:
            if os.getenv(var):
                self.log_check("Security", f"Environment Variable {var}", "PASS", "Set")
            else:
                self.log_check("Security", f"Environment Variable {var}", "WARN", "Not set")
        
        # Check file permissions
        sensitive_files = [
            os.path.join(self.project_dir, "backend", "src", "database", "app.db"),
            os.path.join(self.project_dir, "backend", "requirements.txt")
        ]
        
        for file_path in sensitive_files:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                permissions = oct(stat.st_mode)[-3:]
                if permissions in ['644', '640', '600']:
                    self.log_check("Security", f"File Permissions {os.path.basename(file_path)}", "PASS", f"Mode {permissions}")
                else:
                    self.log_check("Security", f"File Permissions {os.path.basename(file_path)}", "WARN", f"Mode {permissions}")
    
    def check_deployment_files(self):
        """Check deployment configuration files"""
        print("📋 Checking Deployment Files...")
        
        deployment_files = [
            ("docker-compose.yml", "Docker Compose"),
            ("nginx.conf", "Nginx Configuration"),
            ("deploy-production.sh", "Production Deployment Script"),
            ("backup.sh", "Backup Script"),
            ("qryti-learn-api.service", "Systemd Service")
        ]
        
        for filename, description in deployment_files:
            file_path = os.path.join(self.project_dir, filename)
            if os.path.exists(file_path):
                self.log_check("Deployment", description, "PASS", "File exists")
            else:
                self.log_check("Deployment", description, "WARN", "File missing")
        
        # Check if deployment scripts are executable
        scripts = ["deploy-production.sh", "backup.sh"]
        for script in scripts:
            script_path = os.path.join(self.project_dir, script)
            if os.path.exists(script_path) and os.access(script_path, os.X_OK):
                self.log_check("Deployment", f"Script {script} Executable", "PASS", "Executable")
            elif os.path.exists(script_path):
                self.log_check("Deployment", f"Script {script} Executable", "WARN", "Not executable")
    
    def check_documentation(self):
        """Check documentation completeness"""
        print("📚 Checking Documentation...")
        
        docs = [
            ("README.md", "Project README"),
            ("DEPLOYMENT_GUIDE.md", "Deployment Guide"),
            ("API_Documentation.md", "API Documentation"),
            ("User_Guide.md", "User Guide"),
            ("COMPREHENSIVE_API_DOCUMENTATION.md", "Comprehensive API Docs")
        ]
        
        for filename, description in docs:
            file_path = os.path.join(self.project_dir, filename)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                if file_size > 1000:  # At least 1KB
                    self.log_check("Documentation", description, "PASS", f"{file_size} bytes")
                else:
                    self.log_check("Documentation", description, "WARN", "File too small")
            else:
                self.log_check("Documentation", description, "WARN", "File missing")
    
    def check_performance_metrics(self):
        """Check system performance metrics"""
        print("⚡ Checking Performance Metrics...")
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent < 50:
            self.log_check("Performance", "CPU Usage", "PASS", f"{cpu_percent:.1f}%")
        elif cpu_percent < 80:
            self.log_check("Performance", "CPU Usage", "WARN", f"{cpu_percent:.1f}%")
        else:
            self.log_check("Performance", "CPU Usage", "FAIL", f"{cpu_percent:.1f}% (too high)")
        
        # Memory usage
        memory = psutil.virtual_memory()
        if memory.percent < 70:
            self.log_check("Performance", "Memory Usage", "PASS", f"{memory.percent:.1f}%")
        elif memory.percent < 85:
            self.log_check("Performance", "Memory Usage", "WARN", f"{memory.percent:.1f}%")
        else:
            self.log_check("Performance", "Memory Usage", "FAIL", f"{memory.percent:.1f}% (too high)")
        
        # Disk usage
        disk = psutil.disk_usage('/')
        if disk.percent < 80:
            self.log_check("Performance", "Disk Usage", "PASS", f"{disk.percent:.1f}%")
        elif disk.percent < 90:
            self.log_check("Performance", "Disk Usage", "WARN", f"{disk.percent:.1f}%")
        else:
            self.log_check("Performance", "Disk Usage", "FAIL", f"{disk.percent:.1f}% (too high)")
    
    def run_comprehensive_check(self):
        """Run all production readiness checks"""
        print("🚀 Qryti Learn Production Readiness Check")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all checks
        self.check_system_requirements()
        self.check_dependencies()
        self.check_database_integrity()
        self.check_api_endpoints()
        self.check_security_configuration()
        self.check_deployment_files()
        self.check_documentation()
        self.check_performance_metrics()
        
        # Calculate results
        total_checks = len(self.checks)
        passed_checks = len([c for c in self.checks if c['status'] == 'PASS'])
        failed_checks = len([c for c in self.checks if c['status'] == 'FAIL'])
        warning_checks = len([c for c in self.checks if c['status'] == 'WARN'])
        
        success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        # Determine overall readiness
        if len(self.critical_failures) == 0 and success_rate >= 80:
            overall_status = "PRODUCTION READY"
            status_icon = "🎉"
        elif len(self.critical_failures) == 0:
            overall_status = "MOSTLY READY (Minor Issues)"
            status_icon = "⚠️"
        else:
            overall_status = "NOT READY (Critical Issues)"
            status_icon = "❌"
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': overall_status,
            'success_rate': success_rate,
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': failed_checks,
            'warning_checks': warning_checks,
            'critical_failures': len(self.critical_failures),
            'execution_time': time.time() - start_time,
            'checks': self.checks,
            'critical_failures_detail': self.critical_failures,
            'warnings_detail': self.warnings
        }
        
        # Display summary
        print("\n" + "=" * 60)
        print("📊 PRODUCTION READINESS SUMMARY")
        print("=" * 60)
        print(f"{status_icon} Overall Status: {overall_status}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"✅ Passed: {passed_checks}")
        print(f"⚠️ Warnings: {warning_checks}")
        print(f"❌ Failed: {failed_checks}")
        print(f"🚨 Critical Failures: {len(self.critical_failures)}")
        
        if self.critical_failures:
            print("\n🚨 CRITICAL ISSUES TO RESOLVE:")
            for failure in self.critical_failures:
                print(f"  ❌ {failure['category']}: {failure['check']}")
                if failure['details']:
                    print(f"     {failure['details']}")
        
        if self.warnings:
            print(f"\n⚠️ WARNINGS TO CONSIDER ({len(self.warnings)}):")
            for warning in self.warnings[:5]:  # Show first 5 warnings
                print(f"  ⚠️ {warning['category']}: {warning['check']}")
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"/home/ubuntu/projects/production_readiness_report_{timestamp}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"\n❌ Failed to save report: {e}")
        
        return report

def main():
    """Main function"""
    checker = ProductionReadinessChecker()
    return checker.run_comprehensive_check()

if __name__ == "__main__":
    main()

