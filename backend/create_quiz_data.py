#!/usr/bin/env python3
"""
Script to manually create quiz sample data
"""
import sys
import os
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.user import db
from src.models.quiz import Quiz, Question
from src.main import create_app

def create_quiz_data():
    """Create sample quiz data"""
    app = create_app('development')
    
    with app.app_context():
        print("Creating quiz sample data...")
        
        # Import Module model
        from src.models.course import Module
        
        # Check if quizzes already exist
        existing_quizzes = Quiz.query.count()
        print(f"Existing quizzes: {existing_quizzes}")
        
        if existing_quizzes > 0:
            print("Quizzes already exist, skipping creation")
            return
        
        # Get existing modules
        modules = Module.query.all()
        print(f"Found {len(modules)} modules")
        
        if len(modules) == 0:
            print("No modules found, cannot create quizzes")
            return
        
        # Create sample quizzes for the first few modules
        quiz_data = [
            {
                'module_id': modules[0].id if len(modules) > 0 else 1,  # First module
                'title': 'ISO 42001 Foundations Assessment',
                'description': 'Test your understanding of AI governance fundamentals',
                'time_limit_minutes': 30,
                'passing_score': 70,
                'max_attempts': 3,
                'is_active': True,
                'questions': [
                    {
                        'question_text': 'What is the primary purpose of ISO/IEC 42001?',
                        'question_type': 'multiple_choice',
                        'options_json': json.dumps([
                            'To provide guidelines for AI system development',
                            'To establish requirements for AI management systems',
                            'To define AI testing procedures',
                            'To regulate AI market practices'
                        ]),
                        'correct_answers_json': json.dumps(['To establish requirements for AI management systems']),
                        'explanation': 'ISO/IEC 42001 specifies requirements for establishing, implementing, maintaining and continually improving an AI management system.',
                        'points': 10,
                        'order_index': 1
                    },
                    {
                        'question_text': 'Which of the following are key components of an AI management system? (Select all that apply)',
                        'question_type': 'multiple_select',
                        'options_json': json.dumps([
                            'Risk management',
                            'Governance framework',
                            'Performance monitoring',
                            'Marketing strategy'
                        ]),
                        'correct_answers_json': json.dumps(['Risk management', 'Governance framework', 'Performance monitoring']),
                        'explanation': 'AI management systems include risk management, governance frameworks, and performance monitoring, but not marketing strategy.',
                        'points': 15,
                        'order_index': 2
                    },
                    {
                        'question_text': 'Describe the key benefits of implementing ISO/IEC 42001 in an organization.',
                        'question_type': 'case_study',
                        'options_json': json.dumps([]),
                        'correct_answers_json': json.dumps(['Key benefits include improved AI governance, risk management, stakeholder confidence, regulatory compliance, and systematic approach to AI development.']),
                        'explanation': 'ISO/IEC 42001 provides a structured framework for managing AI systems throughout their lifecycle.',
                        'points': 20,
                        'order_index': 3
                    }
                ]
            },
            {
                'module_id': modules[1].id if len(modules) > 1 else modules[0].id,  # Second module or first if only one
                'title': 'ISO 42001 Practitioner Exam',
                'description': 'Advanced assessment for practical implementation knowledge',
                'time_limit_minutes': 45,
                'passing_score': 75,
                'max_attempts': 2,
                'is_active': True,
                'questions': [
                    {
                        'question_text': 'How should AI risks be categorized in an ISO 42001 implementation?',
                        'question_type': 'multiple_choice',
                        'options_json': json.dumps([
                            'By technical complexity only',
                            'By business impact and likelihood',
                            'By development cost',
                            'By team size requirements'
                        ]),
                        'correct_answers_json': json.dumps(['By business impact and likelihood']),
                        'explanation': 'AI risks should be categorized based on their potential business impact and likelihood of occurrence.',
                        'points': 15,
                        'order_index': 1
                    },
                    {
                        'question_text': 'What are the essential elements of an AI risk assessment framework?',
                        'question_type': 'multiple_select',
                        'options_json': json.dumps([
                            'Risk identification',
                            'Impact analysis',
                            'Mitigation strategies',
                            'Budget allocation'
                        ]),
                        'correct_answers_json': json.dumps(['Risk identification', 'Impact analysis', 'Mitigation strategies']),
                        'explanation': 'AI risk assessment includes identification, analysis, and mitigation, but budget allocation is a separate concern.',
                        'points': 20,
                        'order_index': 2
                    }
                ]
            }
        ]
        
        try:
            for quiz_info in quiz_data:
                questions_data = quiz_info.pop('questions')
                
                # Create quiz
                quiz = Quiz(**quiz_info)
                db.session.add(quiz)
                db.session.flush()  # Get the quiz ID
                
                print(f"Created quiz: {quiz.title} (ID: {quiz.id})")
                
                # Create questions
                for q_data in questions_data:
                    question = Question(
                        quiz_id=quiz.id,
                        **q_data
                    )
                    db.session.add(question)
                    print(f"  Added question: {question.question_text[:50]}...")
            
            db.session.commit()
            print("✅ Quiz sample data created successfully!")
            
            # Verify creation
            total_quizzes = Quiz.query.count()
            total_questions = Question.query.count()
            print(f"📊 Total quizzes: {total_quizzes}")
            print(f"📊 Total questions: {total_questions}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating quiz data: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    create_quiz_data()

