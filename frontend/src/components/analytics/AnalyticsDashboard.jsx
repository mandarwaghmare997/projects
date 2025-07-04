import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';

const AnalyticsDashboard = () => {
  const { user } = useAuth();
  const [analyticsData, setAnalyticsData] = useState(null);
  const [detailedData, setDetailedData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('30');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchAnalyticsData();
    fetchDetailedData();
  }, [timeRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await apiService.get(`/analytics/summary?days=${timeRange}`);
      setAnalyticsData(response);
      setError(null);
    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const fetchDetailedData = async () => {
    try {
      const response = await apiService.get(`/analytics/detailed?days=${timeRange}`);
      setDetailedData(response);
    } catch (err) {
      console.error('Error fetching detailed analytics:', err);
    }
  };

  const formatTime = (minutes) => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
  };

  const getStreakColor = (streak) => {
    if (streak >= 30) return 'text-purple-600 bg-purple-100';
    if (streak >= 14) return 'text-green-600 bg-green-100';
    if (streak >= 7) return 'text-blue-600 bg-blue-100';
    if (streak >= 3) return 'text-yellow-600 bg-yellow-100';
    return 'text-gray-600 bg-gray-100';
  };

  const getDayName = (dayIndex) => {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    return days[dayIndex];
  };

  const renderStudyTimeChart = () => {
    if (!analyticsData?.daily_study_time) return null;

    const maxMinutes = Math.max(...analyticsData.daily_study_time.map(d => d.minutes));
    
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Study Time</h3>
        <div className="space-y-2">
          {analyticsData.daily_study_time.slice(-14).map((day, index) => (
            <div key={index} className="flex items-center">
              <div className="w-16 text-sm text-gray-600">
                {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              </div>
              <div className="flex-1 mx-4">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-blue-500 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${maxMinutes > 0 ? (day.minutes / maxMinutes) * 100 : 0}%` }}
                  ></div>
                </div>
              </div>
              <div className="w-16 text-sm text-gray-900 text-right">
                {formatTime(day.minutes)}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderLearningPatterns = () => {
    if (!detailedData?.learning_patterns) return null;

    const { hourly_activity, weekly_activity } = detailedData.learning_patterns;
    
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hourly Activity */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity by Hour</h3>
          <div className="grid grid-cols-6 gap-2">
            {Array.from({ length: 24 }, (_, hour) => {
              const activity = hourly_activity.find(a => a.hour === hour);
              const count = activity ? activity.count : 0;
              const maxCount = Math.max(...hourly_activity.map(a => a.count));
              const intensity = maxCount > 0 ? (count / maxCount) : 0;
              
              return (
                <div
                  key={hour}
                  className={`h-8 rounded text-xs flex items-center justify-center text-white font-medium ${
                    intensity > 0.7 ? 'bg-blue-600' :
                    intensity > 0.4 ? 'bg-blue-400' :
                    intensity > 0.1 ? 'bg-blue-200 text-gray-700' : 'bg-gray-100 text-gray-400'
                  }`}
                  title={`${hour}:00 - ${count} activities`}
                >
                  {hour}
                </div>
              );
            })}
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Darker colors indicate higher activity
          </div>
        </div>

        {/* Weekly Activity */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity by Day</h3>
          <div className="space-y-3">
            {Array.from({ length: 7 }, (_, day) => {
              const activity = weekly_activity.find(a => a.day === day);
              const count = activity ? activity.count : 0;
              const maxCount = Math.max(...weekly_activity.map(a => a.count));
              const percentage = maxCount > 0 ? (count / maxCount) * 100 : 0;
              
              return (
                <div key={day} className="flex items-center">
                  <div className="w-12 text-sm text-gray-600">
                    {getDayName(day)}
                  </div>
                  <div className="flex-1 mx-4">
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        className="bg-green-500 h-3 rounded-full transition-all duration-300"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="w-8 text-sm text-gray-900 text-right">
                    {count}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  };

  const renderAchievements = () => {
    if (!analyticsData?.achievements) return null;

    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Achievements</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {analyticsData.achievements.map((achievement) => (
            <div 
              key={achievement.id} 
              className={`p-4 rounded-lg border-2 transition-all ${
                achievement.completed 
                  ? 'border-green-200 bg-green-50' 
                  : 'border-gray-200 bg-gray-50'
              }`}
            >
              <div className="flex items-center mb-2">
                <span className="text-2xl mr-3">{achievement.icon}</span>
                <div className="flex-1">
                  <h4 className={`font-semibold ${
                    achievement.completed ? 'text-green-800' : 'text-gray-900'
                  }`}>
                    {achievement.title}
                  </h4>
                  <p className="text-sm text-gray-600">{achievement.description}</p>
                </div>
                {achievement.completed && (
                  <div className="text-green-600">
                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                )}
              </div>
              
              <div className="mb-2">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Progress</span>
                  <span className="font-medium">
                    {achievement.current}/{achievement.target}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      achievement.completed ? 'bg-green-500' : 'bg-blue-500'
                    }`}
                    style={{ width: `${achievement.progress_percentage}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderPerformanceMetrics = () => {
    if (!analyticsData?.performance_metrics) return null;

    const metrics = analyticsData.performance_metrics;
    
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Quiz Attempts</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.quiz_attempts}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pass Rate</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.quiz_pass_rate}%</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <svg className="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Score</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.average_score}%</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <svg className="w-6 h-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Modules Done</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.modules_completed}</p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderLearningStreak = () => {
    if (!analyticsData?.learning_streak) return null;

    const streak = analyticsData.learning_streak;
    
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Learning Streak</h3>
        <div className="flex items-center justify-between">
          <div className="text-center">
            <div className={`text-4xl font-bold mb-2 px-4 py-2 rounded-lg ${getStreakColor(streak.current_streak)}`}>
              {streak.current_streak}
            </div>
            <div className="text-sm text-gray-600">Current Streak</div>
            <div className="text-xs text-gray-500">days</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600 mb-2">
              {streak.longest_streak}
            </div>
            <div className="text-sm text-gray-600">Best Streak</div>
            <div className="text-xs text-gray-500">days</div>
          </div>
          
          <div className="flex-1 ml-8">
            <div className="text-sm text-gray-600 mb-2">
              {streak.current_streak >= 7 
                ? "Amazing! Keep up the great work!" 
                : "Study daily to build your streak!"}
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-orange-500 h-3 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(100, (streak.current_streak / 30) * 100)}%` }}
              ></div>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Goal: 30 days
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">
          <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={fetchAnalyticsData}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Learning Analytics</h2>
          <p className="text-gray-600 mt-1">
            Insights into your learning patterns and performance
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="365">Last year</option>
          </select>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', name: 'Overview' },
            { id: 'patterns', name: 'Learning Patterns' },
            { id: 'achievements', name: 'Achievements' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {renderPerformanceMetrics()}
          {renderLearningStreak()}
          {renderStudyTimeChart()}
        </div>
      )}

      {activeTab === 'patterns' && (
        <div className="space-y-6">
          {renderLearningPatterns()}
        </div>
      )}

      {activeTab === 'achievements' && (
        <div className="space-y-6">
          {renderAchievements()}
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;

