import React, { useState } from 'react';
import AnalyticsDashboard from '../components/analytics/AnalyticsDashboard';
import ProgressDashboard from '../components/progress/ProgressDashboard';
import AchievementSystem from '../components/achievements/AchievementSystem';

const AnalyticsPage = () => {
  const [activeTab, setActiveTab] = useState('analytics');

  const tabs = [
    { id: 'analytics', name: 'Analytics', icon: '📊' },
    { id: 'progress', name: 'Progress', icon: '📈' },
    { id: 'achievements', name: 'Achievements', icon: '🏆' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <a href="/dashboard" className="text-blue-600 hover:text-blue-800 transition-colors">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </a>
              <h1 className="ml-4 text-xl font-semibold text-gray-900">Learning Analytics</h1>
            </div>
            <nav className="flex space-x-4">
              <a
                href="/dashboard"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Dashboard
              </a>
              <a
                href="/certificates"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Certificates
              </a>
              <a
                href="/quizzes"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Quizzes
              </a>
              <a
                href="/profile"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Profile
              </a>
            </nav>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'analytics' && <AnalyticsDashboard />}
        {activeTab === 'progress' && <ProgressDashboard />}
        {activeTab === 'achievements' && <AchievementSystem />}
      </div>
    </div>
  );
};

export default AnalyticsPage;

