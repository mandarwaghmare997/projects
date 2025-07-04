import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import apiService from '../../services/api';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { 
  Clock, 
  Target, 
  BookOpen, 
  Trophy, 
  CheckCircle, 
  AlertCircle,
  Play,
  RotateCcw,
  Star,
  Users,
  TrendingUp
} from 'lucide-react';

const QuizList = ({ courseId, onQuizSelect }) => {
  const { user } = useAuth();
  const [quizzes, setQuizzes] = useState([]);
  const [attempts, setAttempts] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadQuizzes();
    loadUserAttempts();
  }, [courseId]);

  const loadQuizzes = async () => {
    try {
      setLoading(true);
      const response = courseId 
        ? await apiService.getCourseQuizzes(courseId)
        : await apiService.getAllQuizzes();
      setQuizzes(response);
    } catch (error) {
      console.error('Failed to load quizzes:', error);
      setError('Failed to load quizzes. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadUserAttempts = async () => {
    try {
      const response = await apiService.getUserQuizAttempts();
      const attemptsMap = {};
      response.forEach(attempt => {
        if (!attemptsMap[attempt.quiz_id]) {
          attemptsMap[attempt.quiz_id] = [];
        }
        attemptsMap[attempt.quiz_id].push(attempt);
      });
      setAttempts(attemptsMap);
    } catch (error) {
      console.error('Failed to load user attempts:', error);
    }
  };

  const getQuizStatus = (quiz) => {
    const quizAttempts = attempts[quiz.id] || [];
    if (quizAttempts.length === 0) {
      return { status: 'not_attempted', message: 'Not attempted' };
    }

    const bestAttempt = quizAttempts.reduce((best, current) => 
      current.score > best.score ? current : best
    );

    const passed = bestAttempt.score >= quiz.passing_score;
    const canRetake = quiz.max_attempts === 0 || quizAttempts.length < quiz.max_attempts;

    if (passed) {
      return { 
        status: 'passed', 
        message: `Passed with ${bestAttempt.score}%`,
        score: bestAttempt.score,
        attempts: quizAttempts.length
      };
    } else if (canRetake) {
      return { 
        status: 'can_retake', 
        message: `Best score: ${bestAttempt.score}% (${quizAttempts.length}/${quiz.max_attempts || '∞'} attempts)`,
        score: bestAttempt.score,
        attempts: quizAttempts.length
      };
    } else {
      return { 
        status: 'failed', 
        message: `Failed - No more attempts`,
        score: bestAttempt.score,
        attempts: quizAttempts.length
      };
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'beginner':
        return 'text-green-600 bg-green-100';
      case 'intermediate':
        return 'text-yellow-600 bg-yellow-100';
      case 'advanced':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'passed':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'can_retake':
        return <RotateCcw className="h-5 w-5 text-yellow-600" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Play className="h-5 w-5 text-blue-600" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading quizzes...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (quizzes.length === 0) {
    return (
      <Card>
        <CardContent className="text-center py-8">
          <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Quizzes Available</h3>
          <p className="text-gray-600">
            {courseId 
              ? 'This course doesn\'t have any quizzes yet.' 
              : 'No quizzes are available at the moment.'
            }
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">
          {courseId ? 'Course Quizzes' : 'Available Quizzes'}
        </h2>
        <div className="text-sm text-gray-600">
          {quizzes.length} quiz{quizzes.length !== 1 ? 'es' : ''} available
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {quizzes.map((quiz) => {
          const status = getQuizStatus(quiz);
          const canTakeQuiz = status.status === 'not_attempted' || status.status === 'can_retake';

          return (
            <Card key={quiz.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg mb-2">{quiz.title}</CardTitle>
                    <CardDescription className="text-sm">
                      {quiz.description}
                    </CardDescription>
                  </div>
                  <div className="ml-4">
                    {getStatusIcon(status.status)}
                  </div>
                </div>

                {quiz.difficulty && (
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(quiz.difficulty)}`}>
                      {quiz.difficulty}
                    </span>
                    {quiz.category && (
                      <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-600">
                        {quiz.category}
                      </span>
                    )}
                  </div>
                )}
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Quiz Stats */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center text-gray-600">
                    <BookOpen className="h-4 w-4 mr-2" />
                    {quiz.question_count || quiz.questions?.length || 0} questions
                  </div>
                  <div className="flex items-center text-gray-600">
                    <Clock className="h-4 w-4 mr-2" />
                    {quiz.time_limit_minutes} min
                  </div>
                  <div className="flex items-center text-gray-600">
                    <Target className="h-4 w-4 mr-2" />
                    {quiz.passing_score}% to pass
                  </div>
                  <div className="flex items-center text-gray-600">
                    <RotateCcw className="h-4 w-4 mr-2" />
                    {quiz.max_attempts === 0 ? 'Unlimited' : quiz.max_attempts} attempts
                  </div>
                </div>

                {/* Status Information */}
                <div className={`p-3 rounded-lg ${
                  status.status === 'passed' 
                    ? 'bg-green-50 border border-green-200' 
                    : status.status === 'failed'
                    ? 'bg-red-50 border border-red-200'
                    : status.status === 'can_retake'
                    ? 'bg-yellow-50 border border-yellow-200'
                    : 'bg-blue-50 border border-blue-200'
                }`}>
                  <div className="flex items-center justify-between">
                    <span className={`text-sm font-medium ${
                      status.status === 'passed' 
                        ? 'text-green-800' 
                        : status.status === 'failed'
                        ? 'text-red-800'
                        : status.status === 'can_retake'
                        ? 'text-yellow-800'
                        : 'text-blue-800'
                    }`}>
                      {status.message}
                    </span>
                    {status.status === 'passed' && (
                      <Trophy className="h-4 w-4 text-yellow-500" />
                    )}
                  </div>
                </div>

                {/* Quiz Statistics */}
                {quiz.stats && (
                  <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                    <div className="flex items-center">
                      <Users className="h-4 w-4 mr-2" />
                      {quiz.stats.total_attempts} attempts
                    </div>
                    <div className="flex items-center">
                      <TrendingUp className="h-4 w-4 mr-2" />
                      {quiz.stats.average_score}% avg
                    </div>
                  </div>
                )}

                {/* Action Button */}
                <Button 
                  onClick={() => onQuizSelect(quiz)}
                  disabled={!canTakeQuiz}
                  className={`w-full ${
                    status.status === 'passed'
                      ? 'bg-green-600 hover:bg-green-700'
                      : status.status === 'can_retake'
                      ? 'bg-yellow-600 hover:bg-yellow-700'
                      : 'bg-blue-600 hover:bg-blue-700'
                  }`}
                >
                  {status.status === 'not_attempted' && (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Start Quiz
                    </>
                  )}
                  {status.status === 'can_retake' && (
                    <>
                      <RotateCcw className="h-4 w-4 mr-2" />
                      Retake Quiz
                    </>
                  )}
                  {status.status === 'passed' && (
                    <>
                      <Trophy className="h-4 w-4 mr-2" />
                      Review Quiz
                    </>
                  )}
                  {status.status === 'failed' && (
                    <>
                      <AlertCircle className="h-4 w-4 mr-2" />
                      No More Attempts
                    </>
                  )}
                </Button>

                {/* Additional Info for Passed Quizzes */}
                {status.status === 'passed' && (
                  <div className="text-center">
                    <div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
                      <div className="flex items-center">
                        <Star className="h-4 w-4 mr-1 text-yellow-500" />
                        Best: {status.score}%
                      </div>
                      <div>
                        Attempts: {status.attempts}
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default QuizList;

