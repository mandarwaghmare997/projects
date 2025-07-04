from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from src.models.user import db

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    time_limit_minutes = db.Column(db.Integer, default=30, nullable=False)
    passing_score = db.Column(db.Integer, default=70, nullable=False)  # Percentage required to pass
    max_attempts = db.Column(db.Integer, default=3, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan', order_by='Question.order_index')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Quiz {self.title}>'

    def to_dict(self, include_questions=False):
        """Convert quiz to dictionary"""
        data = {
            'id': self.id,
            'module_id': self.module_id,
            'title': self.title,
            'description': self.description,
            'time_limit_minutes': self.time_limit_minutes,
            'passing_score': self.passing_score,
            'max_attempts': self.max_attempts,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'question_count': len(self.questions),
            'total_points': sum(q.points for q in self.questions)
        }
        
        if include_questions:
            data['questions'] = [question.to_dict() for question in self.questions]
            
        return data

    def calculate_score(self, answers):
        """Calculate quiz score based on answers"""
        total_points = 0
        earned_points = 0
        
        for question in self.questions:
            total_points += question.points
            if str(question.id) in answers:
                user_answer = answers[str(question.id)]
                if question.check_answer(user_answer):
                    earned_points += question.points
        
        return (earned_points / total_points * 100) if total_points > 0 else 0

    def get_user_attempts(self, user_id):
        """Get user's attempts for this quiz"""
        return QuizAttempt.query.filter_by(quiz_id=self.id, user_id=user_id).order_by(QuizAttempt.started_at.desc()).all()

    def can_attempt(self, user_id):
        """Check if user can attempt this quiz"""
        attempts = self.get_user_attempts(user_id)
        return len(attempts) < self.max_attempts

    def get_average_score(self):
        """Get average score for this quiz across all attempts"""
        from src.models.quiz import QuizAttempt  # Import here to avoid circular import
        attempts = QuizAttempt.query.filter_by(quiz_id=self.id).filter(QuizAttempt.score.isnot(None)).all()
        if not attempts:
            return 0
        total_score = sum(attempt.score for attempt in attempts)
        return round(total_score / len(attempts), 1)

    @staticmethod
    def get_by_module(module_id):
        """Get quizzes by module ID"""
        return Quiz.query.filter_by(module_id=module_id, is_active=True).all()


class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False)  # mcq, multiple_select, case_study, true_false
    options_json = db.Column(db.Text, nullable=True)  # JSON array of options
    correct_answers_json = db.Column(db.Text, nullable=False)  # JSON array of correct answers
    explanation = db.Column(db.Text, nullable=True)
    points = db.Column(db.Integer, default=1, nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Question {self.id}>'

    @property
    def options(self):
        """Get options as Python list"""
        return json.loads(self.options_json) if self.options_json else []

    @options.setter
    def options(self, value):
        """Set options from Python list"""
        self.options_json = json.dumps(value) if value else None

    @property
    def correct_answers(self):
        """Get correct answers as Python list"""
        return json.loads(self.correct_answers_json) if self.correct_answers_json else []

    @correct_answers.setter
    def correct_answers(self, value):
        """Set correct answers from Python list"""
        self.correct_answers_json = json.dumps(value) if value else None

    def to_dict(self, include_answers=False):
        """Convert question to dictionary"""
        data = {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'options': self.options,
            'points': self.points,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_answers:
            data['correct_answers'] = self.correct_answers
            data['explanation'] = self.explanation
            
        return data

    def check_answer(self, user_answer):
        """Check if user answer is correct"""
        correct = self.correct_answers
        
        if self.question_type == 'mcq' or self.question_type == 'true_false':
            return user_answer in correct
        elif self.question_type == 'multiple_select':
            # For multiple select, user must select all correct answers and no incorrect ones
            if isinstance(user_answer, list):
                return set(user_answer) == set(correct)
            return False
        elif self.question_type == 'case_study':
            # Case study questions may have multiple acceptable answers
            return user_answer in correct
        
        return False

    @staticmethod
    def create_mcq(quiz_id, question_text, options, correct_answer, explanation=None, points=1, order_index=1):
        """Create a multiple choice question"""
        question = Question(
            quiz_id=quiz_id,
            question_text=question_text,
            question_type='mcq',
            points=points,
            order_index=order_index,
            explanation=explanation
        )
        question.options = options
        question.correct_answers = [correct_answer]
        return question

    @staticmethod
    def create_multiple_select(quiz_id, question_text, options, correct_answers, explanation=None, points=2, order_index=1):
        """Create a multiple select question"""
        question = Question(
            quiz_id=quiz_id,
            question_text=question_text,
            question_type='multiple_select',
            points=points,
            order_index=order_index,
            explanation=explanation
        )
        question.options = options
        question.correct_answers = correct_answers
        return question


class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Float, nullable=True)  # Percentage score
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=True)
    answers_json = db.Column(db.Text, nullable=True)  # JSON of user answers
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    time_taken_minutes = db.Column(db.Integer, nullable=True)
    passed = db.Column(db.Boolean, nullable=True)

    def __repr__(self):
        return f'<QuizAttempt User:{self.user_id} Quiz:{self.quiz_id}>'

    @property
    def answers(self):
        """Get answers as Python dict"""
        return json.loads(self.answers_json) if self.answers_json else {}

    @answers.setter
    def answers(self, value):
        """Set answers from Python dict"""
        self.answers_json = json.dumps(value) if value else None

    def to_dict(self):
        """Convert quiz attempt to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'score': self.score,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'time_taken_minutes': self.time_taken_minutes,
            'passed': self.passed,
            'quiz': self.quiz.to_dict() if self.quiz else None
        }

    def complete_attempt(self, answers):
        """Complete the quiz attempt with answers"""
        self.answers = answers
        self.completed_at = datetime.utcnow()
        
        # Calculate time taken
        if self.started_at:
            time_diff = self.completed_at - self.started_at
            self.time_taken_minutes = int(time_diff.total_seconds() / 60)
        
        # Calculate score
        self.score = self.quiz.calculate_score(answers)
        self.passed = self.score >= self.quiz.passing_score
        
        # Count correct answers
        correct_count = 0
        for question in self.quiz.questions:
            if str(question.id) in answers:
                user_answer = answers[str(question.id)]
                if question.check_answer(user_answer):
                    correct_count += 1
        
        self.correct_answers = correct_count
        self.total_questions = len(self.quiz.questions)
        
        db.session.commit()
        return self

    @staticmethod
    def start_attempt(user_id, quiz_id):
        """Start a new quiz attempt"""
        quiz = Quiz.query.get(quiz_id)
        if not quiz or not quiz.can_attempt(user_id):
            return None
        
        attempt = QuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            total_questions=len(quiz.questions)
        )
        db.session.add(attempt)
        db.session.commit()
        return attempt

    @staticmethod
    def get_user_attempts(user_id, quiz_id=None):
        """Get user's quiz attempts"""
        query = QuizAttempt.query.filter_by(user_id=user_id)
        if quiz_id:
            query = query.filter_by(quiz_id=quiz_id)
        return query.order_by(QuizAttempt.started_at.desc()).all()

