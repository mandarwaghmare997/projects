import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import apiService from '../../services/api';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  ArrowRight, 
  ArrowLeft,
  RotateCcw,
  Trophy,
  Target,
  BookOpen
} from 'lucide-react';

const QuizInterface = ({ quizId, onQuizComplete }) => {
  const { user } = useAuth();
  const [quiz, setQuiz] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [quizStarted, setQuizStarted] = useState(false);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showExplanation, setShowExplanation] = useState(false);

  useEffect(() => {
    loadQuiz();
  }, [quizId]);

  useEffect(() => {
    let timer;
    if (quizStarted && timeRemaining > 0 && !quizCompleted) {
      timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            handleSubmitQuiz();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [quizStarted, timeRemaining, quizCompleted]);

  const loadQuiz = async () => {
    try {
      setLoading(true);
      const response = await apiService.getQuiz(quizId);
      setQuiz(response);
      setTimeRemaining(response.time_limit_minutes * 60);
    } catch (error) {
      console.error('Failed to load quiz:', error);
      setError('Failed to load quiz. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleStartQuiz = () => {
    setQuizStarted(true);
    setAnswers({});
    setCurrentQuestionIndex(0);
    setShowExplanation(false);
  };

  const handleAnswerSelect = (questionId, selectedOption) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: selectedOption
    }));
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < quiz.questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      setShowExplanation(false);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
      setShowExplanation(false);
    }
  };

  const handleSubmitQuiz = async () => {
    try {
      setLoading(true);
      const response = await apiService.submitQuizAttempt(quizId, {
        answers: answers,
        time_taken: (quiz.time_limit_minutes * 60) - timeRemaining
      });
      
      setResults(response);
      setQuizCompleted(true);
      
      if (onQuizComplete) {
        onQuizComplete(response);
      }
    } catch (error) {
      console.error('Failed to submit quiz:', error);
      setError('Failed to submit quiz. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getAnswerStatus = (questionId, option) => {
    if (!results) return null;
    
    const question = quiz.questions.find(q => q.id === questionId);
    const userAnswer = answers[questionId];
    const correctAnswer = question.correct_answer;
    
    if (option === correctAnswer) {
      return 'correct';
    } else if (option === userAnswer && option !== correctAnswer) {
      return 'incorrect';
    }
    return null;
  };

  const getProgressPercentage = () => {
    const answeredQuestions = Object.keys(answers).length;
    return (answeredQuestions / quiz.questions.length) * 100;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading quiz...</p>
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

  if (!quiz) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>Quiz not found.</AlertDescription>
      </Alert>
    );
  }

  // Quiz Results View
  if (quizCompleted && results) {
    const passed = results.score >= quiz.passing_score;
    
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <Card>
          <CardHeader className="text-center">
            <div className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-4 ${
              passed ? 'bg-green-100' : 'bg-red-100'
            }`}>
              {passed ? (
                <Trophy className="h-8 w-8 text-green-600" />
              ) : (
                <XCircle className="h-8 w-8 text-red-600" />
              )}
            </div>
            <CardTitle className={`text-2xl ${passed ? 'text-green-600' : 'text-red-600'}`}>
              {passed ? 'Congratulations!' : 'Quiz Not Passed'}
            </CardTitle>
            <CardDescription>
              {passed 
                ? 'You have successfully completed the quiz!' 
                : 'You need to score at least ' + quiz.passing_score + '% to pass.'
              }
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{results.score}%</div>
                <div className="text-sm text-gray-600">Your Score</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {results.correct_answers}/{quiz.questions.length}
                </div>
                <div className="text-sm text-gray-600">Correct Answers</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {formatTime(results.time_taken)}
                </div>
                <div className="text-sm text-gray-600">Time Taken</div>
              </div>
            </div>

            {results.feedback && (
              <Alert>
                <Target className="h-4 w-4" />
                <AlertDescription>{results.feedback}</AlertDescription>
              </Alert>
            )}

            <div className="flex justify-center space-x-4">
              <Button 
                onClick={() => setShowExplanation(!showExplanation)}
                variant="outline"
              >
                <BookOpen className="h-4 w-4 mr-2" />
                {showExplanation ? 'Hide' : 'Show'} Explanations
              </Button>
              
              {!passed && (
                <Button 
                  onClick={() => {
                    setQuizCompleted(false);
                    setQuizStarted(false);
                    setAnswers({});
                    setResults(null);
                    setCurrentQuestionIndex(0);
                    setTimeRemaining(quiz.time_limit_minutes * 60);
                  }}
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Retake Quiz
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Question Review */}
        {showExplanation && (
          <div className="space-y-4">
            {quiz.questions.map((question, index) => (
              <Card key={question.id}>
                <CardHeader>
                  <CardTitle className="text-lg">
                    Question {index + 1}: {question.question_text}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {question.options.map((option, optionIndex) => {
                      const status = getAnswerStatus(question.id, optionIndex);
                      return (
                        <div 
                          key={optionIndex}
                          className={`p-3 rounded-lg border ${
                            status === 'correct' 
                              ? 'bg-green-50 border-green-200' 
                              : status === 'incorrect'
                              ? 'bg-red-50 border-red-200'
                              : 'bg-gray-50 border-gray-200'
                          }`}
                        >
                          <div className="flex items-center">
                            {status === 'correct' && <CheckCircle className="h-4 w-4 text-green-600 mr-2" />}
                            {status === 'incorrect' && <XCircle className="h-4 w-4 text-red-600 mr-2" />}
                            <span>{option}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  
                  {question.explanation && (
                    <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">Explanation:</h4>
                      <p className="text-blue-800">{question.explanation}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    );
  }

  // Quiz Start Screen
  if (!quizStarted) {
    return (
      <Card className="max-w-2xl mx-auto">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">{quiz.title}</CardTitle>
          <CardDescription>{quiz.description}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <Clock className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <div className="font-medium">Time Limit</div>
              <div className="text-sm text-gray-600">{quiz.time_limit_minutes} minutes</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <Target className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <div className="font-medium">Passing Score</div>
              <div className="text-sm text-gray-600">{quiz.passing_score}%</div>
            </div>
          </div>

          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="font-medium mb-2">Quiz Information</div>
            <div className="text-sm text-gray-600 space-y-1">
              <div>{quiz.questions.length} questions</div>
              <div>Multiple choice format</div>
              <div>You can navigate between questions</div>
              <div>Submit when ready or time expires</div>
            </div>
          </div>

          <div className="text-center">
            <Button 
              onClick={handleStartQuiz}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              size="lg"
            >
              Start Quiz
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Quiz Taking Interface
  const currentQuestion = quiz.questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === quiz.questions.length - 1;
  const allQuestionsAnswered = Object.keys(answers).length === quiz.questions.length;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Quiz Header */}
      <Card>
        <CardContent className="p-4">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-lg font-semibold">{quiz.title}</h2>
              <p className="text-sm text-gray-600">
                Question {currentQuestionIndex + 1} of {quiz.questions.length}
              </p>
            </div>
            <div className="text-right">
              <div className={`text-lg font-mono ${timeRemaining < 300 ? 'text-red-600' : 'text-gray-700'}`}>
                <Clock className="inline h-4 w-4 mr-1" />
                {formatTime(timeRemaining)}
              </div>
              <div className="text-sm text-gray-600">
                {Object.keys(answers).length} answered
              </div>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${getProgressPercentage()}%` }}
              ></div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Current Question */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">
            {currentQuestion.question_text}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {currentQuestion.options.map((option, index) => (
            <div 
              key={index}
              className={`p-4 rounded-lg border cursor-pointer transition-all ${
                answers[currentQuestion.id] === index
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
              onClick={() => handleAnswerSelect(currentQuestion.id, index)}
            >
              <div className="flex items-center">
                <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                  answers[currentQuestion.id] === index
                    ? 'border-blue-500 bg-blue-500'
                    : 'border-gray-300'
                }`}>
                  {answers[currentQuestion.id] === index && (
                    <div className="w-2 h-2 bg-white rounded-full mx-auto mt-0.5"></div>
                  )}
                </div>
                <span>{option}</span>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Navigation */}
      <Card>
        <CardContent className="p-4">
          <div className="flex justify-between items-center">
            <Button 
              onClick={handlePreviousQuestion}
              disabled={currentQuestionIndex === 0}
              variant="outline"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Previous
            </Button>

            <div className="flex space-x-2">
              {isLastQuestion && allQuestionsAnswered ? (
                <Button 
                  onClick={handleSubmitQuiz}
                  className="bg-green-600 hover:bg-green-700"
                >
                  Submit Quiz
                </Button>
              ) : (
                <Button 
                  onClick={handleNextQuestion}
                  disabled={isLastQuestion}
                >
                  Next
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Question Navigation Grid */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Question Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-5 sm:grid-cols-10 gap-2">
            {quiz.questions.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentQuestionIndex(index)}
                className={`w-8 h-8 rounded text-sm font-medium transition-all ${
                  index === currentQuestionIndex
                    ? 'bg-blue-600 text-white'
                    : answers[quiz.questions[index].id] !== undefined
                    ? 'bg-green-100 text-green-800 border border-green-300'
                    : 'bg-gray-100 text-gray-600 border border-gray-300 hover:bg-gray-200'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>
          <div className="mt-4 flex items-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center">
              <div className="w-4 h-4 bg-blue-600 rounded mr-2"></div>
              Current
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 bg-green-100 border border-green-300 rounded mr-2"></div>
              Answered
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 bg-gray-100 border border-gray-300 rounded mr-2"></div>
              Unanswered
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default QuizInterface;

