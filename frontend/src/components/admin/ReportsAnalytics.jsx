import React, { useState, useEffect } from 'react';

const ReportsAnalytics = () => {
  const [activeReport, setActiveReport] = useState('overview');
  const [reportData, setReportData] = useState({});
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState('30');
  const [exportFormat, setExportFormat] = useState('json');

  useEffect(() => {
    fetchReportData();
  }, [activeReport, dateRange]);

  const fetchReportData = async () => {
    try {
      setLoading(true);
      let endpoint = '';
      
      switch (activeReport) {
        case 'overview':
          endpoint = `/api/reporting/business/kpis?days=${dateRange}`;
          break;
        case 'users':
          endpoint = `/api/reporting/users/overview?days=${dateRange}`;
          break;
        case 'engagement':
          endpoint = `/api/reporting/users/engagement?days=${dateRange}`;
          break;
        case 'content':
          endpoint = `/api/reporting/content/performance`;
          break;
        case 'learning':
          endpoint = `/api/reporting/learning/progress`;
          break;
        case 'cohort':
          endpoint = `/api/reporting/custom/user-cohort?period=month`;
          break;
        default:
          endpoint = `/api/reporting/business/kpis?days=${dateRange}`;
      }

      const response = await fetch(endpoint, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setReportData(data);
      }
    } catch (error) {
      console.error('Error fetching report data:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportReport = async () => {
    try {
      const response = await fetch(`/api/reporting/export/users?format=${exportFormat}&include_progress=true`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        
        // Create downloadable file
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `qryti-learn-report-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error exporting report:', error);
      alert('Failed to export report');
    }
  };

  const MetricCard = ({ title, value, subtitle, trend, color = 'blue' }) => (
    <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
          {trend && (
            <p className={`text-sm mt-1 ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {trend >= 0 ? '↗' : '↘'} {Math.abs(trend)}%
            </p>
          )}
        </div>
      </div>
    </div>
  );

  const TabButton = ({ id, label, isActive, onClick }) => (
    <button
      onClick={() => onClick(id)}
      className={`px-4 py-2 font-medium text-sm rounded-lg transition-colors ${
        isActive
          ? 'bg-blue-600 text-white'
          : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
      }`}
    >
      {label}
    </button>
  );

  const OverviewReport = () => (
    <div className="space-y-6">
      {/* KPI Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="New Users"
          value={reportData.user_metrics?.new_users || 0}
          subtitle={`${dateRange} days`}
          trend={reportData.user_metrics?.user_growth_rate}
        />
        <MetricCard
          title="Active Users"
          value={reportData.user_metrics?.active_users || 0}
          subtitle={`${reportData.user_metrics?.activation_rate || 0}% activation rate`}
        />
        <MetricCard
          title="Course Enrollments"
          value={reportData.engagement_metrics?.course_enrollments || 0}
          subtitle="New enrollments"
        />
        <MetricCard
          title="Certificates Issued"
          value={reportData.engagement_metrics?.certificates_issued || 0}
          subtitle="Achievement rate"
        />
      </div>

      {/* Engagement Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Engagement Metrics</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Quiz Attempts</span>
              <span className="font-semibold">{reportData.engagement_metrics?.quiz_attempts || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Video Views</span>
              <span className="font-semibold">{reportData.engagement_metrics?.video_views || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Resource Downloads</span>
              <span className="font-semibold">{reportData.engagement_metrics?.resource_downloads || 0}</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Learning Outcomes</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Course Completions</span>
              <span className="font-semibold">{reportData.learning_outcomes?.course_completions || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Quiz Pass Rate</span>
              <span className="font-semibold">{reportData.learning_outcomes?.quiz_pass_rate || 0}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Completion Rate</span>
              <span className="font-semibold">{reportData.learning_outcomes?.completion_rate || 0}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const UserReport = () => (
    <div className="space-y-6">
      {/* User Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          title="Total Users"
          value={reportData.overview?.total_users || 0}
          subtitle="All registered users"
        />
        <MetricCard
          title="Active Users"
          value={reportData.overview?.active_users || 0}
          subtitle="Currently active"
        />
        <MetricCard
          title="Engagement Rate"
          value={`${Math.round((reportData.overview?.active_users / reportData.overview?.total_users * 100) || 0)}%`}
          subtitle="User engagement"
        />
      </div>

      {/* User Activity */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">User Activity Breakdown</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">{reportData.overview?.active_last_7_days || 0}</p>
            <p className="text-sm text-gray-600">Active Last 7 Days</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">{reportData.overview?.active_last_30_days || 0}</p>
            <p className="text-sm text-gray-600">Active Last 30 Days</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-purple-600">{reportData.overview?.engagement?.enrolled_users || 0}</p>
            <p className="text-sm text-gray-600">Enrolled in Courses</p>
          </div>
        </div>
      </div>

      {/* New User Trends */}
      {reportData.trends?.new_users && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">New User Registration Trends</h3>
          <div className="space-y-2">
            {reportData.trends.new_users.slice(-7).map((day, index) => (
              <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                <span className="text-sm text-gray-600">{new Date(day.date).toLocaleDateString()}</span>
                <span className="font-semibold">{day.count} new users</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const ContentReport = () => (
    <div className="space-y-6">
      {/* Course Performance */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Course Performance</h3>
        <div className="overflow-x-auto">
          <table className="w-full table-auto">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Course</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Enrollments</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Completions</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rate</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {reportData.courses?.map((course, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-4 py-4 text-sm font-medium text-gray-900">{course.title}</td>
                  <td className="px-4 py-4 text-sm text-gray-600">{course.enrollments}</td>
                  <td className="px-4 py-4 text-sm text-gray-600">{course.completions}</td>
                  <td className="px-4 py-4 text-sm text-gray-600">{course.completion_rate.toFixed(1)}%</td>
                  <td className="px-4 py-4 text-sm text-gray-600">{course.avg_quiz_score.toFixed(1)}</td>
                </tr>
              )) || (
                <tr>
                  <td colSpan="5" className="px-4 py-8 text-center text-gray-500">No course data available</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quiz Performance */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quiz Performance</h3>
        <div className="overflow-x-auto">
          <table className="w-full table-auto">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quiz</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Attempts</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Completions</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Score</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Range</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {reportData.quizzes?.map((quiz, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-4 py-4 text-sm font-medium text-gray-900">{quiz.title}</td>
                  <td className="px-4 py-4 text-sm text-gray-600">{quiz.attempts}</td>
                  <td className="px-4 py-4 text-sm text-gray-600">{quiz.completions}</td>
                  <td className="px-4 py-4 text-sm text-gray-600">{quiz.avg_score.toFixed(1)}</td>
                  <td className="px-4 py-4 text-sm text-gray-600">
                    {quiz.min_score.toFixed(1)} - {quiz.max_score.toFixed(1)}
                  </td>
                </tr>
              )) || (
                <tr>
                  <td colSpan="5" className="px-4 py-8 text-center text-gray-500">No quiz data available</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Resource Performance */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Resource Downloads</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reportData.resources?.map((resource, index) => (
            <div key={index} className="p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">{resource.title}</h4>
              <div className="flex justify-between text-sm text-gray-600">
                <span>{resource.downloads} downloads</span>
                <span>★ {resource.avg_rating.toFixed(1)}</span>
              </div>
            </div>
          )) || <p className="text-gray-500">No resource data available</p>}
        </div>
      </div>
    </div>
  );

  const LearningReport = () => (
    <div className="space-y-6">
      {/* Learning Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard
          title="Total Enrollments"
          value={reportData.overview?.total_enrollments || 0}
          subtitle="All time"
        />
        <MetricCard
          title="Completed Courses"
          value={reportData.overview?.completed_courses || 0}
          subtitle={`${reportData.overview?.completion_rate?.toFixed(1) || 0}% rate`}
        />
        <MetricCard
          title="In Progress"
          value={reportData.overview?.in_progress_courses || 0}
          subtitle="Currently learning"
        />
        <MetricCard
          title="Avg Completion"
          value={`${reportData.overview?.avg_completion_days?.toFixed(0) || 0} days`}
          subtitle="Time to complete"
        />
      </div>

      {/* Learning Paths */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Learning Path Analysis</h3>
        <div className="space-y-4">
          {reportData.learning_paths?.map((path, index) => (
            <div key={index} className="p-4 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-medium text-gray-900">{path.course}</h4>
                <span className="text-sm text-gray-600">{path.completion_rate.toFixed(1)}% completion</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ width: `${path.completion_rate}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-sm text-gray-600 mt-2">
                <span>{path.enrollments} enrolled</span>
                <span>{path.completions} completed</span>
              </div>
            </div>
          )) || <p className="text-gray-500">No learning path data available</p>}
        </div>
      </div>

      {/* Skill Development */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Skill Development Tracking</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {reportData.skill_development?.map((skill, index) => (
            <div key={index} className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">{skill.skill_area}</h4>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-600">Proficiency</span>
                <span className="font-semibold">{skill.avg_proficiency.toFixed(1)}/100</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                <div 
                  className="bg-green-600 h-2 rounded-full" 
                  style={{ width: `${skill.avg_proficiency}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500">{skill.assessments} assessments</p>
            </div>
          )) || <p className="text-gray-500">No skill development data available</p>}
        </div>
      </div>

      {/* Certificates */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Certificate Achievements</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {reportData.certificates?.map((cert, index) => (
            <div key={index} className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="font-medium text-gray-900">{cert.type}</p>
              <p className="text-2xl font-bold text-blue-600">{cert.issued}</p>
              <p className="text-sm text-gray-600">
                {cert.verified} verified ({cert.verification_rate.toFixed(1)}%)
              </p>
            </div>
          )) || <p className="text-gray-500">No certificate data available</p>}
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading reports...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Reports & Analytics</h2>
        <div className="flex items-center space-x-4">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="365">Last year</option>
          </select>
          <button
            onClick={exportReport}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
          >
            Export Report
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="flex flex-wrap gap-2">
          <TabButton
            id="overview"
            label="Business Overview"
            isActive={activeReport === 'overview'}
            onClick={setActiveReport}
          />
          <TabButton
            id="users"
            label="User Analytics"
            isActive={activeReport === 'users'}
            onClick={setActiveReport}
          />
          <TabButton
            id="content"
            label="Content Performance"
            isActive={activeReport === 'content'}
            onClick={setActiveReport}
          />
          <TabButton
            id="learning"
            label="Learning Progress"
            isActive={activeReport === 'learning'}
            onClick={setActiveReport}
          />
          <TabButton
            id="engagement"
            label="Engagement"
            isActive={activeReport === 'engagement'}
            onClick={setActiveReport}
          />
        </div>
      </div>

      {/* Report Content */}
      <div>
        {activeReport === 'overview' && <OverviewReport />}
        {activeReport === 'users' && <UserReport />}
        {activeReport === 'content' && <ContentReport />}
        {activeReport === 'learning' && <LearningReport />}
        {activeReport === 'engagement' && <UserReport />}
      </div>
    </div>
  );
};

export default ReportsAnalytics;

