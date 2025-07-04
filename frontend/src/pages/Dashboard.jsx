import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { 
  BookOpen, 
  Award, 
  Clock, 
  TrendingUp, 
  User, 
  LogOut,
  Play,
  CheckCircle,
  Star,
  Calendar,
  Target
} from 'lucide-react';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [dashboardResponse, coursesResponse] = await Promise.all([
        apiService.getDashboard(),
        apiService.getCourses()
      ]);
      
      setDashboardData(dashboardResponse);
      setCourses(coursesResponse.courses || []);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleEnrollInCourse = async (courseId) => {
    try {
      await apiService.enrollInCourse(courseId);
      // Reload dashboard data to reflect enrollment
      await loadDashboardData();
    } catch (error) {
      console.error('Failed to enroll in course:', error);
      alert('Failed to enroll in course. Please try again.');
    }
  };

  const handleLogout = async () => {
    await logout();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={loadDashboardData}>Try Again</Button>
        </div>
      </div>
    );
  }

  const overview = dashboardData?.overview || {};
  const courseProgress = dashboardData?.course_progress || [];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <img 
                src="/src/assets/qryti-logo.png" 
                alt="Qryti" 
                className="h-8 w-auto"
              />
              <h1 className="ml-4 text-xl font-semibold text-gray-900">
                Qryti Learn Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <User className="h-5 w-5 text-gray-400" />
                <span className="text-sm text-gray-700">
                  {user?.first_name} {user?.last_name}
                </span>
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleLogout}
                className="flex items-center space-x-2"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.first_name}!
          </h2>
          <p className="text-gray-600">
            Continue your ISO/IEC 42001 AI Management Systems certification journey
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <BookOpen className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Courses</p>
                  <p className="text-2xl font-bold text-gray-900">{overview.total_courses || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <CheckCircle className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Completed</p>
                  <p className="text-2xl font-bold text-gray-900">{overview.completed_courses || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Clock className="h-8 w-8 text-purple-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Learning Hours</p>
                  <p className="text-2xl font-bold text-gray-900">{overview.total_learning_time_hours || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <TrendingUp className="h-8 w-8 text-orange-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Completion Rate</p>
                  <p className="text-2xl font-bold text-gray-900">{Math.round(overview.completion_rate || 0)}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* My Courses */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BookOpen className="h-5 w-5 mr-2" />
                My Courses
              </CardTitle>
              <CardDescription>
                Your enrolled courses and progress
              </CardDescription>
            </CardHeader>
            <CardContent>
              {courseProgress.length > 0 ? (
                <div className="space-y-4">
                  {courseProgress.map((item) => (
                    <div key={item.enrollment.course_id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium text-gray-900">
                          {item.enrollment.course_title}
                        </h4>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          item.enrollment.status === 'completed' 
                            ? 'bg-green-100 text-green-800'
                            : item.enrollment.status === 'in_progress'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {item.enrollment.status.replace('_', ' ')}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{ width: `${item.progress?.completion_percentage || 0}%` }}
                            ></div>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            {Math.round(item.progress?.completion_percentage || 0)}% complete
                          </p>
                        </div>
                        <Button size="sm" className="ml-4">
                          <Play className="h-4 w-4 mr-1" />
                          Continue
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-4">No courses enrolled yet</p>
                  <p className="text-sm text-gray-500">
                    Browse available courses below to get started
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Available Courses */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="h-5 w-5 mr-2" />
                Available Courses
              </CardTitle>
              <CardDescription>
                ISO/IEC 42001 certification levels
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {courses.map((course) => {
                  const isEnrolled = courseProgress.some(
                    item => item.enrollment.course_id === course.id
                  );
                  
                  return (
                    <div key={course.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-medium text-gray-900">{course.title}</h4>
                          <p className="text-sm text-gray-600">{course.description}</p>
                        </div>
                        <div className="flex items-center text-sm text-gray-500">
                          <Clock className="h-4 w-4 mr-1" />
                          {course.duration_hours}h
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-sm text-gray-600">
                          <span className="flex items-center">
                            <Star className="h-4 w-4 mr-1 text-yellow-500" />
                            Level {course.level}
                          </span>
                          <span>{course.module_count} modules</span>
                        </div>
                        {isEnrolled ? (
                          <span className="text-sm text-green-600 font-medium">Enrolled</span>
                        ) : (
                          <Button 
                            size="sm" 
                            onClick={() => handleEnrollInCourse(course.id)}
                          >
                            Enroll Now
                          </Button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

