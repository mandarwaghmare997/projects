import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import QuizList from '../components/quiz/QuizList';
import QuizInterface from '../components/quiz/QuizInterface';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { 
  ArrowLeft, 
  BookOpen, 
  Trophy, 
  Target,
  Clock,
  Users
} from 'lucide-react';

const QuizPage = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [quizCompleted, setQuizCompleted] = useState(false);

  const handleQuizSelect = (quiz) => {
    // Navigate to the quiz interface page
    navigate(`/quiz/${quiz.id}`);
  };

  const handleQuizComplete = (results) => {
    setQuizCompleted(true);
    // You could show a success message or redirect here
    console.log('Quiz completed:', results);
  };

  const handleBackToList = () => {
    setSelectedQuiz(null);
    setQuizCompleted(false);
  };

  const handleBackToCourse = () => {
    if (courseId) {
      navigate(`/course/${courseId}`);
    } else {
      navigate('/dashboard');
    }
  };

  if (selectedQuiz) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-6">
            <Button 
              onClick={handleBackToList}
              variant="outline"
              className="mb-4"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Quiz List
            </Button>
            
            <div className="text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {selectedQuiz.title}
              </h1>
              <p className="text-gray-600 max-w-2xl mx-auto">
                {selectedQuiz.description}
              </p>
            </div>
          </div>

          {/* Quiz Interface */}
          <QuizInterface 
            quizId={selectedQuiz.id}
            onQuizComplete={handleQuizComplete}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <Button 
              onClick={handleBackToCourse}
              variant="outline"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              {courseId ? 'Back to Course' : 'Back to Dashboard'}
            </Button>
          </div>

          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              {courseId ? 'Course Assessments' : 'Quiz Center'}
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Test your knowledge and earn certifications with our comprehensive quiz system.
              Track your progress and improve your understanding of ISO/IEC 42001 AI Management Systems.
            </p>
          </div>
        </div>

        {/* Stats Cards */}
        {!courseId && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardContent className="p-6 text-center">
                <BookOpen className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">12</div>
                <div className="text-sm text-gray-600">Total Quizzes</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 text-center">
                <Trophy className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">8</div>
                <div className="text-sm text-gray-600">Completed</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 text-center">
                <Target className="h-8 w-8 text-green-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">85%</div>
                <div className="text-sm text-gray-600">Average Score</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 text-center">
                <Clock className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">2.5h</div>
                <div className="text-sm text-gray-600">Time Spent</div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Quiz Categories */}
        {!courseId && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Quiz Categories</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { name: 'Foundation Level', count: 3, color: 'bg-green-100 text-green-800' },
                { name: 'Practitioner Level', count: 3, color: 'bg-blue-100 text-blue-800' },
                { name: 'Lead Implementer', count: 3, color: 'bg-purple-100 text-purple-800' },
                { name: 'Auditor/Assessor', count: 3, color: 'bg-red-100 text-red-800' },
              ].map((category) => (
                <Card key={category.name} className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-4 text-center">
                    <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium mb-2 ${category.color}`}>
                      {category.name}
                    </div>
                    <div className="text-lg font-semibold text-gray-900">{category.count} Quizzes</div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Quiz List */}
        <QuizList 
          courseId={courseId}
          onQuizSelect={handleQuizSelect}
        />

        {/* Help Section */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Users className="h-5 w-5 mr-2" />
              Need Help?
            </CardTitle>
            <CardDescription>
              Tips for taking quizzes and maximizing your learning experience
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Before You Start</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Review the course materials thoroughly</li>
                  <li>• Ensure you have a stable internet connection</li>
                  <li>• Find a quiet environment to focus</li>
                  <li>• Check the time limit and plan accordingly</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-2">During the Quiz</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Read each question carefully</li>
                  <li>• Use the navigation to review answers</li>
                  <li>• Don't spend too much time on one question</li>
                  <li>• Submit before time runs out</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default QuizPage;

