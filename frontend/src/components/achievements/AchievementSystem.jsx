import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';

const AchievementSystem = () => {
  const { user } = useAuth();
  const [achievements, setAchievements] = useState([]);
  const [milestones, setMilestones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, completed, in-progress

  useEffect(() => {
    fetchAchievements();
    fetchMilestones();
  }, []);

  const fetchAchievements = async () => {
    try {
      setLoading(true);
      const response = await apiService.get('/analytics/summary');
      setAchievements(response.achievements || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching achievements:', err);
      setError('Failed to load achievements');
    } finally {
      setLoading(false);
    }
  };

  const fetchMilestones = async () => {
    try {
      const response = await apiService.get('/progress/dashboard');
      
      // Create milestone data from progress
      const overview = response.overview || {};
      const milestoneData = [
        {
          id: 'first_enrollment',
          title: 'Welcome Aboard!',
          description: 'Enroll in your first course',
          icon: '🚀',
          type: 'enrollment',
          target: 1,
          current: overview.enrolled_courses || 0,
          completed: (overview.enrolled_courses || 0) >= 1,
          reward: 'Welcome Badge'
        },
        {
          id: 'study_time_10h',
          title: 'Dedicated Learner',
          description: 'Study for 10 hours total',
          icon: '📚',
          type: 'time',
          target: 600, // 10 hours in minutes
          current: overview.total_time_minutes || 0,
          completed: (overview.total_time_minutes || 0) >= 600,
          reward: 'Study Badge'
        },
        {
          id: 'first_certificate',
          title: 'Certified Professional',
          description: 'Earn your first certificate',
          icon: '🏆',
          type: 'certificate',
          target: 1,
          current: overview.certificates_earned || 0,
          completed: (overview.certificates_earned || 0) >= 1,
          reward: 'Achievement Badge'
        },
        {
          id: 'course_completion',
          title: 'Course Master',
          description: 'Complete 3 courses',
          icon: '🎓',
          type: 'completion',
          target: 3,
          current: overview.completed_courses || 0,
          completed: (overview.completed_courses || 0) >= 3,
          reward: 'Master Badge'
        },
        {
          id: 'study_time_50h',
          title: 'Learning Champion',
          description: 'Study for 50 hours total',
          icon: '⭐',
          type: 'time',
          target: 3000, // 50 hours in minutes
          current: overview.total_time_minutes || 0,
          completed: (overview.total_time_minutes || 0) >= 3000,
          reward: 'Champion Badge'
        },
        {
          id: 'all_levels',
          title: 'Level Master',
          description: 'Complete courses at all 4 levels',
          icon: '👑',
          type: 'level',
          target: 4,
          current: 0, // Would need to calculate from course data
          completed: false,
          reward: 'Crown Badge'
        }
      ];
      
      setMilestones(milestoneData);
    } catch (err) {
      console.error('Error fetching milestones:', err);
    }
  };

  const getFilteredAchievements = () => {
    if (filter === 'completed') {
      return achievements.filter(a => a.completed);
    } else if (filter === 'in-progress') {
      return achievements.filter(a => !a.completed && a.current > 0);
    }
    return achievements;
  };

  const getFilteredMilestones = () => {
    if (filter === 'completed') {
      return milestones.filter(m => m.completed);
    } else if (filter === 'in-progress') {
      return milestones.filter(m => !m.completed && m.current > 0);
    }
    return milestones;
  };

  const formatProgress = (current, target, type) => {
    if (type === 'time') {
      const formatTime = (minutes) => {
        if (minutes < 60) return `${minutes}m`;
        const hours = Math.floor(minutes / 60);
        const remainingMinutes = minutes % 60;
        return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
      };
      return `${formatTime(current)} / ${formatTime(target)}`;
    }
    return `${current} / ${target}`;
  };

  const getProgressPercentage = (current, target) => {
    return Math.min(100, (current / target) * 100);
  };

  const getBadgeColor = (type) => {
    const colors = {
      enrollment: 'bg-blue-500',
      time: 'bg-green-500',
      certificate: 'bg-yellow-500',
      completion: 'bg-purple-500',
      level: 'bg-red-500',
      default: 'bg-gray-500'
    };
    return colors[type] || colors.default;
  };

  const renderAchievementCard = (achievement) => (
    <div 
      key={achievement.id}
      className={`p-6 rounded-lg border-2 transition-all duration-300 ${
        achievement.completed 
          ? 'border-green-200 bg-green-50 shadow-md' 
          : 'border-gray-200 bg-white hover:shadow-md'
      }`}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center">
          <span className="text-3xl mr-4">{achievement.icon}</span>
          <div>
            <h3 className={`text-lg font-semibold ${
              achievement.completed ? 'text-green-800' : 'text-gray-900'
            }`}>
              {achievement.title}
            </h3>
            <p className="text-sm text-gray-600 mt-1">{achievement.description}</p>
          </div>
        </div>
        {achievement.completed && (
          <div className="flex items-center text-green-600">
            <svg className="w-6 h-6 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm font-medium">Completed</span>
          </div>
        )}
      </div>

      <div className="mb-4">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-600">Progress</span>
          <span className="font-medium">
            {achievement.current}/{achievement.target}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className={`h-3 rounded-full transition-all duration-500 ${
              achievement.completed ? 'bg-green-500' : 'bg-blue-500'
            }`}
            style={{ width: `${achievement.progress_percentage}%` }}
          ></div>
        </div>
      </div>

      {achievement.completed && (
        <div className="text-center">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            🎉 Achievement Unlocked!
          </span>
        </div>
      )}
    </div>
  );

  const renderMilestoneCard = (milestone) => (
    <div 
      key={milestone.id}
      className={`p-6 rounded-lg border-2 transition-all duration-300 ${
        milestone.completed 
          ? 'border-yellow-200 bg-yellow-50 shadow-md' 
          : 'border-gray-200 bg-white hover:shadow-md'
      }`}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center">
          <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white text-xl mr-4 ${
            milestone.completed ? 'bg-yellow-500' : getBadgeColor(milestone.type)
          }`}>
            {milestone.icon}
          </div>
          <div>
            <h3 className={`text-lg font-semibold ${
              milestone.completed ? 'text-yellow-800' : 'text-gray-900'
            }`}>
              {milestone.title}
            </h3>
            <p className="text-sm text-gray-600 mt-1">{milestone.description}</p>
            <p className="text-xs text-gray-500 mt-1">Reward: {milestone.reward}</p>
          </div>
        </div>
        {milestone.completed && (
          <div className="flex items-center text-yellow-600">
            <svg className="w-6 h-6 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3l14 9-14 9V3z" />
            </svg>
            <span className="text-sm font-medium">Earned</span>
          </div>
        )}
      </div>

      <div className="mb-4">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-600">Progress</span>
          <span className="font-medium">
            {formatProgress(milestone.current, milestone.target, milestone.type)}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className={`h-3 rounded-full transition-all duration-500 ${
              milestone.completed ? 'bg-yellow-500' : getBadgeColor(milestone.type)
            }`}
            style={{ width: `${getProgressPercentage(milestone.current, milestone.target)}%` }}
          ></div>
        </div>
      </div>

      {milestone.completed && (
        <div className="text-center">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
            🏅 Milestone Reached!
          </span>
        </div>
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading achievements...</p>
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
          onClick={fetchAchievements}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  const filteredAchievements = getFilteredAchievements();
  const filteredMilestones = getFilteredMilestones();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Achievements & Milestones</h2>
          <p className="text-gray-600 mt-1">
            Track your learning accomplishments and unlock rewards
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <label htmlFor="filter" className="text-sm font-medium text-gray-700">
            Filter:
          </label>
          <select
            id="filter"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All</option>
            <option value="completed">Completed</option>
            <option value="in-progress">In Progress</option>
          </select>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Achievements Earned</p>
              <p className="text-2xl font-bold text-gray-900">
                {achievements.filter(a => a.completed).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <svg className="w-6 h-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3l14 9-14 9V3z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Milestones Reached</p>
              <p className="text-2xl font-bold text-gray-900">
                {milestones.filter(m => m.completed).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">In Progress</p>
              <p className="text-2xl font-bold text-gray-900">
                {[...achievements, ...milestones].filter(item => !item.completed && item.current > 0).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Achievements Section */}
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Achievements</h3>
        {filteredAchievements.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredAchievements.map(renderAchievementCard)}
          </div>
        ) : (
          <div className="text-center py-8">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No achievements found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {filter === 'completed' ? 'Complete activities to earn achievements.' : 'Start learning to unlock achievements.'}
            </p>
          </div>
        )}
      </div>

      {/* Milestones Section */}
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Learning Milestones</h3>
        {filteredMilestones.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredMilestones.map(renderMilestoneCard)}
          </div>
        ) : (
          <div className="text-center py-8">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M5 3l14 9-14 9V3z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No milestones found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {filter === 'completed' ? 'Reach milestones to see them here.' : 'Start your learning journey to unlock milestones.'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AchievementSystem;

