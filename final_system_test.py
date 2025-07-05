#!/usr/bin/env python3
"""
Final System Test for Qryti Learn
Comprehensive testing of all features before deployment
"""

import requests
import json
import time
from datetime import datetime

class FinalSystemTest:
    def __init__(self):
        self.base_url = "http://localhost:5002"
        self.test_results = []
        self.auth_token = None
        
    def log_test(self, category, test_name, result, status="success", details=None):
        """Log test result"""
        self.test_results.append({
            'category': category,
            'test_name': test_name,
            'result': result,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        status_icon = "✅" if status == "success" else "⚠️" if status == "warning" else "❌"
        print(f"{status_icon} {category}: {test_name} - {result}")
        if details:
            print(f"   📝 {details}")
    
    def test_health_endpoints(self):
        """Test system health endpoints"""
        print("🏥 Testing Health Endpoints...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check",
                    "API Health",
                    f"Healthy - {data.get('status', 'unknown')}",
                    "success",
                    f"Version: {data.get('version', 'unknown')}"
                )
            else:
                self.log_test(
                    "Health Check",
                    "API Health",
                    f"Failed - Status {response.status_code}",
                    "error"
                )
        except Exception as e:
            self.log_test(
                "Health Check",
                "API Health",
                f"Connection failed: {str(e)}",
                "error"
            )
    
    def test_authentication_system(self):
        """Test complete authentication flow"""
        print("🔐 Testing Authentication System...")
        
        # Test user registration
        test_user = {
            "email": f"test_{int(time.time())}@qryti.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            # Register user
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=test_user,
                timeout=10
            )
            
            if response.status_code == 201:
                self.log_test(
                    "Authentication",
                    "User Registration",
                    "Success",
                    "success",
                    f"User created: {test_user['email']}"
                )
                
                # Test login
                login_data = {
                    "email": test_user["email"],
                    "password": test_user["password"]
                }
                
                login_response = requests.post(
                    f"{self.base_url}/api/auth/login",
                    json=login_data,
                    timeout=10
                )
                
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    self.auth_token = login_result.get('access_token')
                    self.log_test(
                        "Authentication",
                        "User Login",
                        "Success",
                        "success",
                        "JWT token received"
                    )
                else:
                    self.log_test(
                        "Authentication",
                        "User Login",
                        f"Failed - Status {login_response.status_code}",
                        "error"
                    )
            else:
                self.log_test(
                    "Authentication",
                    "User Registration",
                    f"Failed - Status {response.status_code}",
                    "warning",
                    "May be due to database permissions"
                )
        except Exception as e:
            self.log_test(
                "Authentication",
                "Auth System",
                f"Error: {str(e)}",
                "error"
            )
    
    def test_core_apis(self):
        """Test core API endpoints"""
        print("🔧 Testing Core APIs...")
        
        # Test courses API
        try:
            response = requests.get(f"{self.base_url}/api/courses", timeout=5)
            if response.status_code == 200:
                courses = response.json()
                self.log_test(
                    "Core APIs",
                    "Courses API",
                    f"Success - {len(courses)} courses",
                    "success"
                )
            else:
                self.log_test(
                    "Core APIs",
                    "Courses API",
                    f"Failed - Status {response.status_code}",
                    "error"
                )
        except Exception as e:
            self.log_test(
                "Core APIs",
                "Courses API",
                f"Error: {str(e)}",
                "error"
            )
        
        # Test quizzes API
        try:
            response = requests.get(f"{self.base_url}/api/quizzes", timeout=5)
            if response.status_code == 200:
                quizzes = response.json()
                quiz_count = len(quizzes) if isinstance(quizzes, list) else "unknown"
                self.log_test(
                    "Core APIs",
                    "Quizzes API",
                    f"Success - {quiz_count} quizzes",
                    "success"
                )
            else:
                self.log_test(
                    "Core APIs",
                    "Quizzes API",
                    f"Failed - Status {response.status_code}",
                    "error"
                )
        except Exception as e:
            self.log_test(
                "Core APIs",
                "Quizzes API",
                f"Error: {str(e)}",
                "error"
            )
    
    def test_enterprise_features(self):
        """Test enterprise and admin features"""
        print("🏢 Testing Enterprise Features...")
        
        # Test admin stats
        try:
            response = requests.get(f"{self.base_url}/api/admin/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                self.log_test(
                    "Enterprise",
                    "Admin Stats",
                    "Success",
                    "success",
                    f"Stats retrieved: {len(stats)} metrics"
                )
            else:
                self.log_test(
                    "Enterprise",
                    "Admin Stats",
                    f"Status {response.status_code}",
                    "warning"
                )
        except Exception as e:
            self.log_test(
                "Enterprise",
                "Admin Stats",
                f"Error: {str(e)}",
                "error"
            )
        
        # Test analytics
        try:
            response = requests.get(f"{self.base_url}/api/analytics/summary", timeout=5)
            if response.status_code == 200:
                analytics = response.json()
                self.log_test(
                    "Enterprise",
                    "Analytics API",
                    "Success",
                    "success",
                    f"Analytics data: {len(analytics)} metrics"
                )
            else:
                self.log_test(
                    "Enterprise",
                    "Analytics API",
                    f"Status {response.status_code}",
                    "warning"
                )
        except Exception as e:
            self.log_test(
                "Enterprise",
                "Analytics API",
                f"Error: {str(e)}",
                "error"
            )
    
    def test_certificate_system(self):
        """Test certificate generation and verification"""
        print("🏆 Testing Certificate System...")
        
        # Test certificate stats
        try:
            response = requests.get(f"{self.base_url}/api/certificates/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                self.log_test(
                    "Certificates",
                    "Certificate Stats",
                    "Success",
                    "success",
                    f"Stats: {stats}"
                )
            else:
                self.log_test(
                    "Certificates",
                    "Certificate Stats",
                    f"Status {response.status_code}",
                    "warning"
                )
        except Exception as e:
            self.log_test(
                "Certificates",
                "Certificate Stats",
                f"Error: {str(e)}",
                "error"
            )
        
        # Test certificate verification
        try:
            response = requests.get(f"{self.base_url}/api/certificates/verify/TEST123", timeout=5)
            if response.status_code in [200, 404]:  # 404 is expected for non-existent cert
                self.log_test(
                    "Certificates",
                    "Certificate Verification",
                    "Endpoint working",
                    "success",
                    "Verification system operational"
                )
            else:
                self.log_test(
                    "Certificates",
                    "Certificate Verification",
                    f"Status {response.status_code}",
                    "warning"
                )
        except Exception as e:
            self.log_test(
                "Certificates",
                "Certificate Verification",
                f"Error: {str(e)}",
                "error"
            )
    
    def test_knowledge_base(self):
        """Test knowledge base and video features"""
        print("📚 Testing Knowledge Base...")
        
        # Test knowledge base stats
        try:
            response = requests.get(f"{self.base_url}/api/knowledge/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                self.log_test(
                    "Knowledge Base",
                    "KB Stats",
                    "Success",
                    "success",
                    f"Resources: {stats.get('total_resources', 0)}, Categories: {stats.get('total_categories', 0)}"
                )
            else:
                self.log_test(
                    "Knowledge Base",
                    "KB Stats",
                    f"Status {response.status_code}",
                    "warning"
                )
        except Exception as e:
            self.log_test(
                "Knowledge Base",
                "KB Stats",
                f"Error: {str(e)}",
                "error"
            )
        
        # Test video stats
        try:
            response = requests.get(f"{self.base_url}/api/videos/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                self.log_test(
                    "Knowledge Base",
                    "Video Stats",
                    "Success",
                    "success",
                    f"Videos: {stats.get('total_videos', 0)}"
                )
            else:
                self.log_test(
                    "Knowledge Base",
                    "Video Stats",
                    f"Status {response.status_code}",
                    "warning"
                )
        except Exception as e:
            self.log_test(
                "Knowledge Base",
                "Video Stats",
                f"Error: {str(e)}",
                "error"
            )
    
    def test_performance_metrics(self):
        """Test system performance"""
        print("⚡ Testing Performance Metrics...")
        
        # Test response times
        endpoints = [
            "/health",
            "/api/courses",
            "/api/quizzes",
            "/api/certificates/stats",
            "/api/knowledge/stats"
        ]
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to ms
                
                if response.status_code == 200 and response_time < 1000:  # Under 1 second
                    self.log_test(
                        "Performance",
                        f"Response Time {endpoint}",
                        f"{response_time:.0f}ms",
                        "success"
                    )
                elif response.status_code == 200:
                    self.log_test(
                        "Performance",
                        f"Response Time {endpoint}",
                        f"{response_time:.0f}ms (slow)",
                        "warning"
                    )
                else:
                    self.log_test(
                        "Performance",
                        f"Response Time {endpoint}",
                        f"Failed - Status {response.status_code}",
                        "error"
                    )
            except Exception as e:
                self.log_test(
                    "Performance",
                    f"Response Time {endpoint}",
                    f"Error: {str(e)}",
                    "error"
                )
    
    def generate_final_report(self):
        """Generate comprehensive final test report"""
        print("\n" + "="*70)
        print("📊 FINAL SYSTEM TEST REPORT")
        print("="*70)
        
        # Categorize results
        categories = {}
        for result in self.test_results:
            category = result['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # Print results by category
        for category, results in categories.items():
            print(f"\n🔧 {category.upper()}")
            print("-" * 50)
            for result in results:
                status_icon = "✅" if result['status'] == "success" else "⚠️" if result['status'] == "warning" else "❌"
                print(f"  {status_icon} {result['test_name']}: {result['result']}")
                if result['details']:
                    print(f"     📝 {result['details']}")
        
        # Generate summary
        total_tests = len(self.test_results)
        successful_tests = [r for r in self.test_results if r['status'] == 'success']
        warning_tests = [r for r in self.test_results if r['status'] == 'warning']
        failed_tests = [r for r in self.test_results if r['status'] == 'error']
        
        print(f"\n📈 SUMMARY")
        print("-" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Successful: {len(successful_tests)}")
        print(f"⚠️ Warnings: {len(warning_tests)}")
        print(f"❌ Failed: {len(failed_tests)}")
        print(f"Success Rate: {(len(successful_tests)/total_tests)*100:.1f}%")
        
        # Overall system status
        if len(failed_tests) == 0 and len(warning_tests) <= 2:
            print(f"\n🎉 SYSTEM STATUS: READY FOR PRODUCTION")
        elif len(failed_tests) <= 2:
            print(f"\n⚠️ SYSTEM STATUS: MOSTLY READY (Minor issues)")
        else:
            print(f"\n❌ SYSTEM STATUS: NEEDS ATTENTION")
        
        # Save detailed report
        report_data = {
            'summary': {
                'total_tests': total_tests,
                'successful_tests': len(successful_tests),
                'warning_tests': len(warning_tests),
                'failed_tests': len(failed_tests),
                'success_rate': (len(successful_tests)/total_tests)*100,
                'generated_at': datetime.now().isoformat()
            },
            'test_results': self.test_results,
            'categories': categories
        }
        
        report_file = f"/home/ubuntu/projects/final_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        return report_data
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Final System Testing")
        print("="*70)
        
        self.test_health_endpoints()
        self.test_authentication_system()
        self.test_core_apis()
        self.test_enterprise_features()
        self.test_certificate_system()
        self.test_knowledge_base()
        self.test_performance_metrics()
        
        return self.generate_final_report()

if __name__ == "__main__":
    tester = FinalSystemTest()
    tester.run_all_tests()

