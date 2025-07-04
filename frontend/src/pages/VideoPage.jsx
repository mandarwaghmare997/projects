import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, BookOpen, Users, Clock, Award } from 'lucide-react';
import VideoPlayer from '../components/video/VideoPlayer';
import VideoList from '../components/video/VideoList';
import apiService from '../services/api';

const VideoPage = () => {
  const { courseId, moduleId } = useParams();
  const navigate = useNavigate();
  
  const [course, setCourse] = useState(null);
  const [module, setModule] = useState(null);
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [progressSummary, setProgressSummary] = useState(null);

  useEffect(() => {
    if (courseId) {
      fetchCourseData();
      fetchProgressSummary();
    }
  }, [courseId, moduleId]);

  const fetchCourseData = async () => {
    try {
      setLoading(true);
      
      // Fetch course details
      const courseResponse = await apiService.get(`/courses/${courseId}`);
      setCourse(courseResponse);
      
      // Fetch module details if moduleId is provided
      if (moduleId) {
        const moduleResponse = await apiService.get(`/courses/${courseId}/modules/${moduleId}`);
        setModule(moduleResponse);
      }
      
    } catch (err) {
      setError('Failed to load course data');
      console.error('Error fetching course data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchProgressSummary = async () => {
    try {
      const response = await apiService.get(`/videos/progress/summary?course_id=${courseId}`);
      setProgressSummary(response);
    } catch (err) {
      console.error('Error fetching progress summary:', err);
    }
  };

  const handleVideoSelect = (video) => {
    setSelectedVideo(video);
  };

  const handleProgressUpdate = async (progressData) => {
    if (!selectedVideo) return;

    try {
      await apiService.post(`/videos/${selectedVideo.id}/progress`, progressData);
      
      // Refresh progress summary
      fetchProgressSummary();
      
      // Update selected video progress locally
      if (selectedVideo.progress) {
        setSelectedVideo(prev => ({
          ...prev,
          progress: {
            ...prev.progress,
            current_position_seconds: progressData.current_position_seconds || prev.progress.current_position_seconds,
            completion_percentage: progressData.completion_percentage || prev.progress.completion_percentage
          }
        }));
      }
    } catch (err) {
      console.error('Error updating video progress:', err);
    }
  };

  const handleBookmarkToggle = async () => {
    if (!selectedVideo) return;

    try {
      const response = await apiService.post(`/videos/${selectedVideo.id}/bookmark`);
      
      // Update selected video bookmark status
      setSelectedVideo(prev => ({
        ...prev,
        progress: {
          ...prev.progress,
          is_bookmarked: response.is_bookmarked
        }
      }));
    } catch (err) {
      console.error('Error toggling bookmark:', err);
    }
  };

  const handleBackToCourse = () => {
    if (moduleId) {
      navigate(`/courses/${courseId}`);
    } else {
      navigate('/dashboard');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-300 rounded w-1/3"></div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <div className="h-96 bg-gray-300 rounded-lg"></div>
              </div>
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-24 bg-gray-300 rounded-lg"></div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchCourseData}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={handleBackToCourse}
            className="flex items-center text-blue-600 hover:text-blue-800 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to {module ? 'Course' : 'Dashboard'}
          </button>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {module ? module.title : course?.title} - Videos
              </h1>
              <p className="text-gray-600 mt-2">
                {module ? module.description : course?.description}
              </p>
            </div>
            
            {/* Progress Summary */}
            {progressSummary && (
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-blue-600">
                      {progressSummary.completed_videos}
                    </div>
                    <div className="text-sm text-gray-600">Completed</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-green-600">
                      {Math.round(progressSummary.completion_rate)}%
                    </div>
                    <div className="text-sm text-gray-600">Progress</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Course/Module Stats */}
        {(course || module) && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center">
                <BookOpen className="w-8 h-8 text-blue-500 mr-3" />
                <div>
                  <div className="text-2xl font-bold text-gray-900">
                    {progressSummary?.total_videos || 0}
                  </div>
                  <div className="text-sm text-gray-600">Total Videos</div>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center">
                <Clock className="w-8 h-8 text-green-500 mr-3" />
                <div>
                  <div className="text-2xl font-bold text-gray-900">
                    {progressSummary?.total_watch_time_formatted || '0m'}
                  </div>
                  <div className="text-sm text-gray-600">Watch Time</div>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center">
                <Award className="w-8 h-8 text-yellow-500 mr-3" />
                <div>
                  <div className="text-2xl font-bold text-gray-900">
                    {progressSummary?.bookmarked_videos || 0}
                  </div>
                  <div className="text-sm text-gray-600">Bookmarked</div>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center">
                <Users className="w-8 h-8 text-purple-500 mr-3" />
                <div>
                  <div className="text-2xl font-bold text-gray-900">
                    {Math.round(progressSummary?.average_completion_percentage || 0)}%
                  </div>
                  <div className="text-sm text-gray-600">Avg. Progress</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Video Player */}
          <div className="lg:col-span-2">
            {selectedVideo ? (
              <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                <VideoPlayer
                  video={selectedVideo}
                  onProgressUpdate={handleProgressUpdate}
                  onBookmarkToggle={handleBookmarkToggle}
                  autoplay={false}
                  showControls={true}
                />
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Select a Video to Start Learning
                </h3>
                <p className="text-gray-600">
                  Choose a video from the list to begin your learning journey.
                </p>
              </div>
            )}
          </div>

          {/* Video List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Course Videos
              </h3>
              
              <VideoList
                courseId={courseId}
                moduleId={moduleId}
                onVideoSelect={handleVideoSelect}
                selectedVideoId={selectedVideo?.id}
              />
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        {progressSummary?.recent_activity && progressSummary.recent_activity.length > 0 && (
          <div className="mt-8">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Recent Activity
              </h3>
              
              <div className="space-y-3">
                {progressSummary.recent_activity.map((activity, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <div className="font-medium text-gray-900">
                        {activity.video_title}
                      </div>
                      <div className="text-sm text-gray-600">
                        {Math.round(activity.completion_percentage)}% completed
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      {activity.last_watched_at && 
                        new Date(activity.last_watched_at).toLocaleDateString()
                      }
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoPage;

