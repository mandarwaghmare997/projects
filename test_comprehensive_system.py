#!/usr/bin/env python3
"""
Comprehensive System Testing for Qryti Learn
Tests all major features and API endpoints
"""

import requests
import json
import time
from datetime import datetime

class QrytiLearnTester:
    def __init__(self, base_url="http://localhost:5002"):
        self.base_url = base_url
        self.test_results = []
        self.access_token = None
        
    def log_test(self, test_name, status, message="", response_time=None):
        """Log test result"""
        result = {
            'test_name': test_name,
            'status': status,
            'message': message,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {message}")
        
    def test_endpoint(self, method, endpoint, data=None, headers=None, expected_status=200):
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == expected_status:
                return True, response.json() if response.content else {}, response_time
            else:
                return False, f"Expected {expected_status}, got {response.status_code}", response_time
                
        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            return False, str(e), response_time
    
    def test_health_check(self):
        """Test health check endpoint"""
        success, data, response_time = self.test_endpoint("GET", "/health")
        if success:
            self.log_test("Health Check", "PASS", f"Service healthy ({response_time}ms)", response_time)
        else:
            self.log_test("Health Check", "FAIL", f"Health check failed: {data}", response_time)
    
    def test_authentication(self):
        """Test authentication endpoints"""
        # Test user registration
        test_user = {
            "email": "test@qryti.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        success, data, response_time = self.test_endpoint("POST", "/api/auth/register", test_user, expected_status=201)
        if success:
            self.log_test("User Registration", "PASS", f"User registered successfully ({response_time}ms)", response_time)
        else:
            self.log_test("User Registration", "WARN", f"Registration may already exist: {data}", response_time)
        
        # Test user login
        login_data = {
            "email": "test@qryti.com",
            "password": "testpass123"
        }
        
        success, data, response_time = self.test_endpoint("POST", "/api/auth/login", login_data)
        if success and 'access_token' in data:
            self.access_token = data['access_token']
            self.log_test("User Login", "PASS", f"Login successful ({response_time}ms)", response_time)
        else:
            self.log_test("User Login", "FAIL", f"Login failed: {data}", response_time)
    
    def test_courses_api(self):
        """Test courses API endpoints"""
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else None
        
        # Test get courses
        success, data, response_time = self.test_endpoint("GET", "/api/courses", headers=headers)
        if success:
            course_count = len(data.get('courses', []))
            self.log_test("Get Courses", "PASS", f"Retrieved {course_count} courses ({response_time}ms)", response_time)
        else:
            self.log_test("Get Courses", "FAIL", f"Failed to get courses: {data}", response_time)
    
    def test_quizzes_api(self):
        """Test quizzes API endpoints"""
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else None
        
        # Test get quizzes
        success, data, response_time = self.test_endpoint("GET", "/api/quizzes", headers=headers)
        if success:
            if isinstance(data, list):
                quiz_count = len(data)
            else:
                quiz_count = len(data.get('quizzes', []))
            self.log_test("Get Quizzes", "PASS", f"Retrieved {quiz_count} quizzes ({response_time}ms)", response_time)
        else:
            self.log_test("Get Quizzes", "FAIL", f"Failed to get quizzes: {data}", response_time)
    
    def test_certificates_api(self):
        """Test certificates API endpoints"""
        # Test public certificate stats
        success, data, response_time = self.test_endpoint("GET", "/api/certificates/stats")
        if success:
            self.log_test("Certificate Stats", "PASS", f"Certificate stats retrieved ({response_time}ms)", response_time)
        else:
            self.log_test("Certificate Stats", "FAIL", f"Failed to get certificate stats: {data}", response_time)
        
        # Test certificate verification (public endpoint)
        success, data, response_time = self.test_endpoint("GET", "/api/certificates/verify/TEST123", expected_status=404)
        if success or "not found" in str(data).lower():
            self.log_test("Certificate Verification", "PASS", f"Verification endpoint working ({response_time}ms)", response_time)
        else:
            self.log_test("Certificate Verification", "FAIL", f"Verification failed: {data}", response_time)
    
    def test_analytics_api(self):
        """Test analytics API endpoints"""
        # Test analytics summary
        success, data, response_time = self.test_endpoint("GET", "/api/analytics/summary")
        if success:
            self.log_test("Analytics Summary", "PASS", f"Analytics data retrieved ({response_time}ms)", response_time)
        else:
            self.log_test("Analytics Summary", "FAIL", f"Failed to get analytics: {data}", response_time)
    
    def test_videos_api(self):
        """Test videos API endpoints"""
        # Test video stats
        success, data, response_time = self.test_endpoint("GET", "/api/videos/stats")
        if success:
            self.log_test("Video Stats", "PASS", f"Video stats retrieved ({response_time}ms)", response_time)
        else:
            self.log_test("Video Stats", "FAIL", f"Failed to get video stats: {data}", response_time)
    
    def test_knowledge_base_api(self):
        """Test knowledge base API endpoints"""
        # Test knowledge base stats
        success, data, response_time = self.test_endpoint("GET", "/api/knowledge/stats")
        if success:
            self.log_test("Knowledge Base Stats", "PASS", f"KB stats retrieved ({response_time}ms)", response_time)
        else:
            self.log_test("Knowledge Base Stats", "FAIL", f"Failed to get KB stats: {data}", response_time)
    
    def test_admin_api(self):
        """Test admin API endpoints"""
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else None
        
        # Test admin stats (requires authentication)
        success, data, response_time = self.test_endpoint("GET", "/api/admin/stats", headers=headers, expected_status=401)
        if success or "authorization" in str(data).lower():
            self.log_test("Admin Stats", "PASS", f"Admin endpoint secured ({response_time}ms)", response_time)
        else:
            self.log_test("Admin Stats", "FAIL", f"Admin security issue: {data}", response_time)
    
    def test_enterprise_api(self):
        """Test enterprise API endpoints"""
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else None
        
        # Test enterprise organizations (requires authentication)
        success, data, response_time = self.test_endpoint("GET", "/api/enterprise/organizations", headers=headers, expected_status=401)
        if success or "authorization" in str(data).lower():
            self.log_test("Enterprise Organizations", "PASS", f"Enterprise endpoint secured ({response_time}ms)", response_time)
        else:
            self.log_test("Enterprise Organizations", "FAIL", f"Enterprise security issue: {data}", response_time)
    
    def test_branding_api(self):
        """Test branding API endpoints"""
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else None
        
        # Test branding settings (requires authentication)
        success, data, response_time = self.test_endpoint("GET", "/api/branding/settings", headers=headers, expected_status=401)
        if success or "authorization" in str(data).lower():
            self.log_test("Branding Settings", "PASS", f"Branding endpoint secured ({response_time}ms)", response_time)
        else:
            self.log_test("Branding Settings", "FAIL", f"Branding security issue: {data}", response_time)
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Qryti Learn System Tests")
        print("=" * 60)
        
        # Core system tests
        self.test_health_check()
        self.test_authentication()
        
        # Feature API tests
        self.test_courses_api()
        self.test_quizzes_api()
        self.test_certificates_api()
        self.test_analytics_api()
        self.test_videos_api()
        self.test_knowledge_base_api()
        
        # Enterprise API tests
        self.test_admin_api()
        self.test_enterprise_api()
        self.test_branding_api()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warning_tests = len([t for t in self.test_results if t['status'] == 'WARN'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warning_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Calculate average response time
        response_times = [t['response_time'] for t in self.test_results if t['response_time']]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"Average Response Time: {avg_response_time:.2f}ms")
        
        # Show failed tests
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.test_results:
                if test['status'] == 'FAIL':
                    print(f"  - {test['test_name']}: {test['message']}")
        
        # Save results to file
        with open('/home/ubuntu/projects/test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: test_results.json")

if __name__ == "__main__":
    tester = QrytiLearnTester()
    tester.run_all_tests()

