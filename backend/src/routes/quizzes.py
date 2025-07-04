from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from src.models.user import User, db
from src.models.course import CourseEnrollment
from src.models.quiz import Quiz, Question, QuizAttempt
from src.models.progress import LearningAnalytics

quizzes_bp = Blueprint('quizzes', __name__)

@quizzes_bp.route('/', methods=['GET'])
def get_all_quizzes():
    """Get all available quizzes (public endpoint)"""
    try:
        quizzes = Quiz.query.filter_by(is_active=True).all()
        
        quizzes_data = []
        for quiz in quizzes:
            quiz_data = quiz.to_dict()
            # Add some basic stats
            quiz_data['question_count'] = len(quiz.questions)
            quiz_data['stats'] = {
                'total_attempts': QuizAttempt.query.filter_by(quiz_id=quiz.id).count(),
                'average_score': quiz.get_average_score()
            }
            quizzes_data.append(quiz_data)
        
        return jsonify(quizzes_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Get all quizzes error: {str(e)}")
        return jsonify({'error': 'Failed to get quizzes'}), 500

@quizzes_bp.route('/<int:quiz_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz_attempt(quiz_id):
    """Submit quiz attempt directly (alternative to attempt-based submission)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        quiz = Quiz.query.get(quiz_id)
        if not quiz or not quiz.is_active:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Check if user can attempt
        if not quiz.can_attempt(current_user_id):
            return jsonify({'error': 'Maximum attempts reached'}), 400
        
        answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)
        
        # Create and complete attempt in one go
        attempt = QuizAttempt.create_and_complete(
            user_id=current_user_id,
            quiz_id=quiz_id,
            answers=answers,
            time_taken_seconds=time_taken
        )
        
        if not attempt:
            return jsonify({'error': 'Failed to submit quiz'}), 500
        
        # Log quiz completion event
        LearningAnalytics.log_event(
            user_id=current_user_id,
            event_type='quiz_completed',
            event_data={
                'quiz_id': quiz_id,
                'attempt_id': attempt.id,
                'score': attempt.score,
                'passed': attempt.passed,
                'time_taken_minutes': attempt.time_taken_minutes
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        # Return detailed results
        results = {
            'score': attempt.score,
            'passed': attempt.passed,
            'correct_answers': attempt.correct_answers,
            'total_questions': len(quiz.questions),
            'time_taken': time_taken,
            'feedback': attempt.get_feedback(),
            'attempt_id': attempt.id
        }
        
        return jsonify(results), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Submit quiz attempt error: {str(e)}")
        return jsonify({'error': 'Failed to submit quiz'}), 500

@quizzes_bp.route('/module/<int:module_id>', methods=['GET'])
@jwt_required()
def get_module_quizzes(module_id):
    """Get all quizzes for a module"""
    try:
        current_user_id = get_jwt_identity()
        
        quizzes = Quiz.get_by_module(module_id)
        
        # Add user attempt information
        quizzes_data = []
        for quiz in quizzes:
            quiz_data = quiz.to_dict()
            attempts = quiz.get_user_attempts(current_user_id)
            quiz_data['user_attempts'] = len(attempts)
            quiz_data['can_attempt'] = quiz.can_attempt(current_user_id)
            quiz_data['best_score'] = max([a.score for a in attempts if a.score is not None], default=None)
            quizzes_data.append(quiz_data)
        
        return jsonify({
            'quizzes': quizzes_data,
            'total': len(quizzes_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get module quizzes error: {str(e)}")
        return jsonify({'error': 'Failed to get quizzes'}), 500

@quizzes_bp.route('/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz(quiz_id):
    """Get quiz details with questions"""
    try:
        current_user_id = get_jwt_identity()
        
        quiz = Quiz.query.get(quiz_id)
        if not quiz or not quiz.is_active:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Check if user can access this quiz (enrolled in course)
        # This is a simplified check - in production, verify module access
        
        attempts = quiz.get_user_attempts(current_user_id)
        
        return jsonify({
            'quiz': quiz.to_dict(include_questions=True),
            'user_attempts': len(attempts),
            'can_attempt': quiz.can_attempt(current_user_id),
            'attempts_history': [attempt.to_dict() for attempt in attempts[:5]]  # Last 5 attempts
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get quiz error: {str(e)}")
        return jsonify({'error': 'Failed to get quiz'}), 500

@quizzes_bp.route('/<int:quiz_id>/start', methods=['POST'])
@jwt_required()
def start_quiz(quiz_id):
    """Start a new quiz attempt"""
    try:
        current_user_id = get_jwt_identity()
        
        quiz = Quiz.query.get(quiz_id)
        if not quiz or not quiz.is_active:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Check if user can attempt
        if not quiz.can_attempt(current_user_id):
            return jsonify({'error': 'Maximum attempts reached'}), 400
        
        # Start new attempt
        attempt = QuizAttempt.start_attempt(current_user_id, quiz_id)
        if not attempt:
            return jsonify({'error': 'Failed to start quiz attempt'}), 500
        
        # Log quiz start event
        LearningAnalytics.log_event(
            user_id=current_user_id,
            event_type='quiz_started',
            event_data={
                'quiz_id': quiz_id,
                'quiz_title': quiz.title,
                'attempt_id': attempt.id
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        # Return quiz with questions but without correct answers
        quiz_data = quiz.to_dict(include_questions=True)
        # Remove correct answers from questions
        for question in quiz_data['questions']:
            question.pop('correct_answers', None)
            question.pop('explanation', None)
        
        return jsonify({
            'message': 'Quiz attempt started',
            'attempt': attempt.to_dict(),
            'quiz': quiz_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Start quiz error: {str(e)}")
        return jsonify({'error': 'Failed to start quiz'}), 500

@quizzes_bp.route('/attempts/<int:attempt_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(attempt_id):
    """Submit quiz answers"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        attempt = QuizAttempt.query.get(attempt_id)
        if not attempt or attempt.user_id != current_user_id:
            return jsonify({'error': 'Quiz attempt not found'}), 404
        
        if attempt.completed_at:
            return jsonify({'error': 'Quiz already submitted'}), 400
        
        answers = data.get('answers', {})
        
        # Complete the attempt
        attempt.complete_attempt(answers)
        
        # Log quiz completion event
        LearningAnalytics.log_event(
            user_id=current_user_id,
            event_type='quiz_completed',
            event_data={
                'quiz_id': attempt.quiz_id,
                'attempt_id': attempt.id,
                'score': attempt.score,
                'passed': attempt.passed,
                'time_taken_minutes': attempt.time_taken_minutes
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'message': 'Quiz submitted successfully',
            'attempt': attempt.to_dict(),
            'passed': attempt.passed
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Submit quiz error: {str(e)}")
        return jsonify({'error': 'Failed to submit quiz'}), 500

@quizzes_bp.route('/attempts/<int:attempt_id>/results', methods=['GET'])
@jwt_required()
def get_quiz_results(attempt_id):
    """Get detailed quiz results"""
    try:
        current_user_id = get_jwt_identity()
        
        attempt = QuizAttempt.query.get(attempt_id)
        if not attempt or attempt.user_id != current_user_id:
            return jsonify({'error': 'Quiz attempt not found'}), 404
        
        if not attempt.completed_at:
            return jsonify({'error': 'Quiz not completed yet'}), 400
        
        # Get detailed results with correct answers
        quiz = attempt.quiz
        results = {
            'attempt': attempt.to_dict(),
            'quiz': quiz.to_dict(),
            'questions_results': []
        }
        
        user_answers = attempt.answers
        for question in quiz.questions:
            question_result = {
                'question': question.to_dict(include_answers=True),
                'user_answer': user_answers.get(str(question.id)),
                'is_correct': question.check_answer(user_answers.get(str(question.id))),
                'points_earned': question.points if question.check_answer(user_answers.get(str(question.id))) else 0
            }
            results['questions_results'].append(question_result)
        
        return jsonify(results), 200
        
    except Exception as e:
        current_app.logger.error(f"Get quiz results error: {str(e)}")
        return jsonify({'error': 'Failed to get quiz results'}), 500

@quizzes_bp.route('/my-attempts', methods=['GET'])
@jwt_required()
def get_my_attempts():
    """Get current user's quiz attempts"""
    try:
        current_user_id = get_jwt_identity()
        
        attempts = QuizAttempt.get_user_attempts(current_user_id)
        
        return jsonify({
            'attempts': [attempt.to_dict() for attempt in attempts],
            'total': len(attempts)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get my attempts error: {str(e)}")
        return jsonify({'error': 'Failed to get quiz attempts'}), 500

