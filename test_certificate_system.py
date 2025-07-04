#!/usr/bin/env python3
"""
Test script for Qryti Learn Certificate System
Tests certificate generation, verification, and PDF creation
"""

import sys
import os
import json
from datetime import datetime

# Add the backend src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from main import create_app
from models.user import db, User
from models.course import Course
from models.progress import Certificate
from utils.certificate_generator import CertificateGenerator

def test_certificate_system():
    """Test the complete certificate system"""
    print("🧪 Testing Qryti Learn Certificate System")
    print("=" * 50)
    
    # Create Flask app context
    app = create_app('development')
    
    with app.app_context():
        try:
            # Test 1: Create a test user and course
            print("\n1. Creating test user and course...")
            
            # Create test user
            test_user = User(
                email='certtest@qryti.com',
                first_name='Certificate',
                last_name='Tester',
                password_hash='test_hash',
                organization='Qryti Test Lab',
                role='student'
            )
            db.session.add(test_user)
            db.session.commit()
            print(f"✅ Created test user: {test_user.email}")
            
            # Get first course
            course = Course.query.first()
            if not course:
                print("❌ No courses found in database")
                return False
            print(f"✅ Using course: {course.title}")
            
            # Test 2: Generate certificate
            print("\n2. Testing certificate generation...")
            
            certificate_generator = CertificateGenerator()
            
            # Create certificate record
            certificate = Certificate(
                user_id=test_user.id,
                course_id=course.id,
                certificate_id=f"QRYTI-{datetime.now().strftime('%Y%m%d')}-001",
                verification_code="TEST123456",
                final_score=85.5
            )
            db.session.add(certificate)
            db.session.commit()
            print(f"✅ Created certificate record: {certificate.certificate_id}")
            
            # Test 3: Generate PDF certificate
            print("\n3. Testing PDF certificate generation...")
            
            try:
                pdf_path = certificate_generator.generate_certificate(
                    user_name=f"{test_user.first_name} {test_user.last_name}",
                    course_title=course.title,
                    certificate_id=certificate.certificate_id,
                    verification_code=certificate.verification_code,
                    completion_date=certificate.issued_at,
                    final_score=certificate.final_score
                )
                
                if pdf_path and os.path.exists(pdf_path):
                    print(f"✅ PDF certificate generated: {pdf_path}")
                    print(f"   File size: {os.path.getsize(pdf_path)} bytes")
                    
                    # Update certificate with PDF path
                    certificate.pdf_path = pdf_path
                    db.session.commit()
                else:
                    print("❌ PDF certificate generation failed")
                    return False
                    
            except Exception as e:
                print(f"❌ PDF generation error: {str(e)}")
                return False
            
            # Test 4: Test certificate verification
            print("\n4. Testing certificate verification...")
            
            # Verify by certificate ID
            found_cert = Certificate.query.filter_by(
                certificate_id=certificate.certificate_id,
                is_valid=True
            ).first()
            
            if found_cert:
                print(f"✅ Certificate verification successful")
                print(f"   Certificate ID: {found_cert.certificate_id}")
                print(f"   Verification Code: {found_cert.verification_code}")
                print(f"   User: {test_user.first_name} {test_user.last_name}")
                print(f"   Course: {course.title}")
                print(f"   Score: {found_cert.final_score}%")
                print(f"   Issued: {found_cert.issued_at}")
            else:
                print("❌ Certificate verification failed")
                return False
            
            # Test 5: Test certificate statistics
            print("\n5. Testing certificate statistics...")
            
            total_certificates = Certificate.query.filter_by(is_valid=True).count()
            recent_certificates = Certificate.query.filter(
                Certificate.issued_at >= datetime.now().replace(day=1)
            ).count()
            
            print(f"✅ Certificate statistics:")
            print(f"   Total valid certificates: {total_certificates}")
            print(f"   Recent certificates (this month): {recent_certificates}")
            
            # Test 6: Test QR code generation
            print("\n6. Testing QR code generation...")
            
            try:
                qr_code_path = certificate_generator.generate_qr_code(
                    verification_url=f"https://qryti.com/verify/{certificate.certificate_id}",
                    certificate_id=certificate.certificate_id
                )
                
                if qr_code_path and os.path.exists(qr_code_path):
                    print(f"✅ QR code generated: {qr_code_path}")
                    print(f"   File size: {os.path.getsize(qr_code_path)} bytes")
                else:
                    print("❌ QR code generation failed")
                    
            except Exception as e:
                print(f"❌ QR code generation error: {str(e)}")
            
            print("\n" + "=" * 50)
            print("🎉 Certificate System Test Completed Successfully!")
            print("✅ All core certificate features are working correctly")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_certificate_system()
    sys.exit(0 if success else 1)

