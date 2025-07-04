from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import os

from src.models.user import User, db
from src.models.course import Course, CourseEnrollment
from src.models.progress import Certificate, LearningAnalytics
from src.utils.certificate_generator import create_certificate

certificates_bp = Blueprint('certificates', __name__)

@certificates_bp.route('/my-certificates', methods=['GET'])
@jwt_required()
def get_my_certificates():
    """Get current user's certificates"""
    try:
        current_user_id = int(get_jwt_identity())  # Convert string to int
        
        certificates = Certificate.get_user_certificates(current_user_id)
        
        return jsonify({
            'certificates': [cert.to_dict() for cert in certificates],
            'total': len(certificates)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get my certificates error: {str(e)}")
        return jsonify({'error': 'Failed to get certificates'}), 500

@certificates_bp.route('/generate/<int:course_id>', methods=['POST'])
@jwt_required()
def generate_certificate(course_id):
    """Generate certificate for completed course"""
    try:
        current_user_id = int(get_jwt_identity())  # Convert string to int
        
        # Check if user completed the course
        enrollment = CourseEnrollment.query.filter_by(
            user_id=current_user_id, 
            course_id=course_id,
            status='completed'
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Course not completed or not enrolled'}), 400
        
        # Check if certificate already exists
        existing_cert = Certificate.query.filter_by(
            user_id=current_user_id, 
            course_id=course_id
        ).first()
        
        if existing_cert:
            return jsonify({
                'message': 'Certificate already exists',
                'certificate': existing_cert.to_dict()
            }), 200
        
        # Create certificate
        certificate = Certificate.create_certificate(
            user_id=current_user_id,
            course_id=course_id,
            final_score=enrollment.final_score or 0
        )
        
        # Generate PDF certificate
        try:
            user = User.query.get(current_user_id)
            course = Course.query.get(course_id)
            
            pdf_path = create_certificate(
                user=user,
                course=course,
                certificate_id=certificate.certificate_id,
                final_score=certificate.final_score,
                completion_date=certificate.issued_date
            )
            
            # Store PDF path in certificate record
            certificate.pdf_path = pdf_path
            db.session.commit()
            
        except Exception as pdf_error:
            current_app.logger.error(f"PDF generation error: {str(pdf_error)}")
            # Continue without PDF if generation fails
        
        # Log certificate generation event
        LearningAnalytics.log_event(
            user_id=current_user_id,
            event_type='certificate_generated',
            event_data={
                'course_id': course_id,
                'certificate_id': certificate.certificate_id,
                'final_score': certificate.final_score
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'message': 'Certificate generated successfully',
            'certificate': certificate.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Generate certificate error: {str(e)}")
        return jsonify({'error': 'Failed to generate certificate'}), 500

@certificates_bp.route('/<certificate_id>', methods=['GET'])
def get_certificate(certificate_id):
    """Get certificate details (public endpoint)"""
    try:
        certificate = Certificate.query.filter_by(certificate_id=certificate_id).first()
        
        if not certificate:
            return jsonify({'error': 'Certificate not found'}), 404
        
        return jsonify({
            'certificate': certificate.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get certificate error: {str(e)}")
        return jsonify({'error': 'Failed to get certificate'}), 500

@certificates_bp.route('/verify/<certificate_id>', methods=['GET'])
def verify_certificate(certificate_id):
    """Verify certificate authenticity (public endpoint)"""
    try:
        certificate = Certificate.verify_certificate(certificate_id)
        
        if not certificate:
            return jsonify({
                'valid': False,
                'message': 'Certificate not found, expired, or revoked'
            }), 404
        
        return jsonify({
            'valid': True,
            'certificate': {
                'certificate_id': certificate.certificate_id,
                'user_name': certificate.user.get_full_name(),
                'course_title': certificate.course.title,
                'course_level': certificate.course.get_level_name(),
                'final_score': certificate.final_score,
                'issued_at': certificate.issued_at.isoformat(),
                'expires_at': certificate.expires_at.isoformat() if certificate.expires_at else None,
                'organization': certificate.user.organization
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Verify certificate error: {str(e)}")
        return jsonify({'error': 'Failed to verify certificate'}), 500

@certificates_bp.route('/verify-code', methods=['POST'])
def verify_by_code():
    """Verify certificate by verification code (public endpoint)"""
    try:
        data = request.get_json()
        verification_code = data.get('verification_code')
        
        if not verification_code:
            return jsonify({'error': 'Verification code is required'}), 400
        
        certificate = Certificate.verify_by_code(verification_code.upper())
        
        if not certificate:
            return jsonify({
                'valid': False,
                'message': 'Invalid verification code or certificate expired/revoked'
            }), 404
        
        return jsonify({
            'valid': True,
            'certificate': {
                'certificate_id': certificate.certificate_id,
                'user_name': certificate.user.get_full_name(),
                'course_title': certificate.course.title,
                'course_level': certificate.course.get_level_name(),
                'final_score': certificate.final_score,
                'issued_at': certificate.issued_at.isoformat(),
                'expires_at': certificate.expires_at.isoformat() if certificate.expires_at else None,
                'organization': certificate.user.organization
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Verify by code error: {str(e)}")
        return jsonify({'error': 'Failed to verify certificate'}), 500

@certificates_bp.route('/course/<int:course_id>/eligible', methods=['GET'])
@jwt_required()
def check_certificate_eligibility(course_id):
    """Check if user is eligible for certificate"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check enrollment and completion status
        enrollment = CourseEnrollment.query.filter_by(
            user_id=current_user_id, 
            course_id=course_id
        ).first()
        
        if not enrollment:
            return jsonify({
                'eligible': False,
                'reason': 'Not enrolled in course'
            }), 200
        
        if enrollment.status != 'completed':
            return jsonify({
                'eligible': False,
                'reason': 'Course not completed',
                'enrollment_status': enrollment.status
            }), 200
        
        # Check if certificate already exists
        existing_cert = Certificate.query.filter_by(
            user_id=current_user_id, 
            course_id=course_id
        ).first()
        
        if existing_cert:
            return jsonify({
                'eligible': True,
                'already_generated': True,
                'certificate': existing_cert.to_dict()
            }), 200
        
        return jsonify({
            'eligible': True,
            'already_generated': False,
            'final_score': enrollment.final_score,
            'completed_at': enrollment.completed_at.isoformat() if enrollment.completed_at else None
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Check certificate eligibility error: {str(e)}")
        return jsonify({'error': 'Failed to check certificate eligibility'}), 500

@certificates_bp.route('/stats', methods=['GET'])
def get_certificate_stats():
    """Get certificate statistics (public endpoint)"""
    try:
        total_certificates = Certificate.query.filter_by(is_valid=True).count()
        
        # Certificates by course level
        certs_by_level = {}
        for level in range(1, 5):
            count = db.session.query(Certificate).join(Course)\
                .filter(Course.level == level, Certificate.is_valid == True).count()
            certs_by_level[f'level_{level}'] = count
        
        # Recent certificates (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_certificates = Certificate.query.filter(
            Certificate.issued_at >= thirty_days_ago,
            Certificate.is_valid == True
        ).count()
        
        return jsonify({
            'total_certificates': total_certificates,
            'certificates_by_level': certs_by_level,
            'recent_certificates_30_days': recent_certificates
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get certificate stats error: {str(e)}")
        return jsonify({'error': 'Failed to get certificate statistics'}), 500

# Admin endpoints
@certificates_bp.route('/admin/revoke/<certificate_id>', methods=['POST'])
@jwt_required()
def revoke_certificate(certificate_id):
    """Revoke a certificate (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        certificate = Certificate.query.filter_by(certificate_id=certificate_id).first()
        
        if not certificate:
            return jsonify({'error': 'Certificate not found'}), 404
        
        certificate.revoke()
        
        # Log revocation event
        LearningAnalytics.log_event(
            user_id=current_user_id,
            event_type='certificate_revoked',
            event_data={
                'certificate_id': certificate_id,
                'revoked_user_id': certificate.user_id
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'message': 'Certificate revoked successfully',
            'certificate': certificate.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Revoke certificate error: {str(e)}")
        return jsonify({'error': 'Failed to revoke certificate'}), 500

@certificates_bp.route('/<certificate_id>/download', methods=['GET'])
@jwt_required()
def download_certificate_pdf(certificate_id):
    """Download certificate PDF"""
    try:
        current_user_id = int(get_jwt_identity())  # Convert string to int
        
        # Find the certificate
        certificate = Certificate.query.filter_by(certificate_id=certificate_id).first()
        
        if not certificate:
            return jsonify({'error': 'Certificate not found'}), 404
        
        # Check if user owns this certificate
        if certificate.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if PDF exists
        if not certificate.pdf_path or not os.path.exists(certificate.pdf_path):
            # Try to regenerate PDF
            try:
                user = User.query.get(current_user_id)
                course = Course.query.get(certificate.course_id)
                
                pdf_path = create_certificate(
                    user=user,
                    course=course,
                    certificate_id=certificate.certificate_id,
                    final_score=certificate.final_score,
                    completion_date=certificate.issued_date
                )
                
                certificate.pdf_path = pdf_path
                db.session.commit()
                
            except Exception as regen_error:
                current_app.logger.error(f"PDF regeneration error: {str(regen_error)}")
                return jsonify({'error': 'Certificate PDF not available'}), 404
        
        # Send the PDF file
        filename = f"certificate_{certificate.certificate_id}.pdf"
        return send_file(
            certificate.pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        current_app.logger.error(f"Download certificate PDF error: {str(e)}")
        return jsonify({'error': 'Failed to download certificate'}), 500

