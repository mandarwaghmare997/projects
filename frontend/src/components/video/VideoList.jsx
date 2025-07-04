import React, { useState, useEffect } from 'react';
import { Play, Clock, BookmarkCheck, CheckCircle, Eye } from 'lucide-react';
import apiService from '../../services/api';

const VideoList = ({ courseId, moduleId, onVideoSelect, selectedVideoId }) => {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, completed, bookmarked, in-progress

  useEffect(() => {
    fetchVideos();
  }, [courseId, moduleId]);

  const fetchVideos = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      if (courseId) params.append('course_id', courseId);
      if (moduleId) params.append('module_id', moduleId);

      const response = await apiService.get(`/videos?${params.toString()}`);
      setVideos(response.videos || []);
    } catch (err) {
      setError('Failed to load videos');
      console.error('Error fetching videos:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredVideos = videos.filter(video => {
    switch (filter) {
      case 'completed':
        return video.progress?.is_completed;
      case 'bookmarked':
        return video.progress?.is_bookmarked;
      case 'in-progress':
        return video.progress && !video.progress.is_completed && video.progress.completion_percentage > 0;
      default:
        return true;
    }
  });

  const getVideoStatus = (video) => {
    if (!video.progress) return 'not-started';
    if (video.progress.is_completed) return 'completed';
    if (video.progress.completion_percentage > 0) return 'in-progress';
    return 'not-started';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'in-progress':
        return <Play className="w-5 h-5 text-blue-500" />;
      default:
        return <Eye className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'border-green-200 bg-green-50';
      case 'in-progress':
        return 'border-blue-200 bg-blue-50';
      default:
        return 'border-gray-200 bg-white';
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, index) => (
          <div key={index} className="animate-pulse">
            <div className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg">
              <div className="w-32 h-20 bg-gray-300 rounded"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-300 rounded w-3/4"></div>
                <div className="h-3 bg-gray-300 rounded w-1/2"></div>
                <div className="h-2 bg-gray-300 rounded w-1/4"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={fetchVideos}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="text-center py-8">
        <Eye className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No videos available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filter Tabs */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        {[
          { key: 'all', label: 'All Videos', count: videos.length },
          { key: 'in-progress', label: 'In Progress', count: videos.filter(v => v.progress && !v.progress.is_completed && v.progress.completion_percentage > 0).length },
          { key: 'completed', label: 'Completed', count: videos.filter(v => v.progress?.is_completed).length },
          { key: 'bookmarked', label: 'Bookmarked', count: videos.filter(v => v.progress?.is_bookmarked).length }
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              filter === tab.key
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label}
            {tab.count > 0 && (
              <span className={`ml-2 px-2 py-0.5 text-xs rounded-full ${
                filter === tab.key ? 'bg-blue-100 text-blue-600' : 'bg-gray-200 text-gray-600'
              }`}>
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Video List */}
      <div className="space-y-4">
        {filteredVideos.map((video, index) => {
          const status = getVideoStatus(video);
          const isSelected = selectedVideoId === video.id;
          
          return (
            <div
              key={video.id}
              onClick={() => onVideoSelect(video)}
              className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                isSelected 
                  ? 'border-blue-500 bg-blue-50 shadow-md' 
                  : `border ${getStatusColor(status)} hover:border-gray-300`
              } rounded-lg overflow-hidden`}
            >
              <div className="flex items-center space-x-4 p-4">
                {/* Video Thumbnail */}
                <div className="relative flex-shrink-0">
                  <img
                    src={video.thumbnail_url || `https://img.youtube.com/vi/${video.youtube_id}/mqdefault.jpg`}
                    alt={video.title}
                    className="w-32 h-20 object-cover rounded-md"
                  />
                  
                  {/* Play Button Overlay */}
                  <div className="absolute inset-0 flex items-center justify-center bg-black/30 rounded-md opacity-0 hover:opacity-100 transition-opacity">
                    <Play className="w-8 h-8 text-white" fill="white" />
                  </div>
                  
                  {/* Duration Badge */}
                  <div className="absolute bottom-1 right-1 bg-black/80 text-white text-xs px-1.5 py-0.5 rounded">
                    {video.duration_formatted}
                  </div>
                  
                  {/* Status Badge */}
                  <div className="absolute top-1 left-1">
                    {getStatusIcon(status)}
                  </div>
                </div>

                {/* Video Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className={`text-lg font-semibold truncate ${
                        isSelected ? 'text-blue-900' : 'text-gray-900'
                      }`}>
                        {video.title}
                      </h3>
                      
                      {video.description && (
                        <p className="text-gray-600 text-sm mt-1 line-clamp-2">
                          {video.description}
                        </p>
                      )}
                      
                      {/* Video Metadata */}
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                        <span className="flex items-center">
                          <Clock className="w-4 h-4 mr-1" />
                          {video.duration_formatted}
                        </span>
                        
                        <span className="capitalize">
                          {video.video_type}
                        </span>
                        
                        <span className="capitalize">
                          {video.difficulty_level}
                        </span>
                        
                        {video.progress?.is_bookmarked && (
                          <span className="flex items-center text-yellow-600">
                            <BookmarkCheck className="w-4 h-4 mr-1" />
                            Bookmarked
                          </span>
                        )}
                      </div>
                      
                      {/* Tags */}
                      {video.tags && video.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {video.tags.slice(0, 3).map((tag, tagIndex) => (
                            <span
                              key={tagIndex}
                              className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full"
                            >
                              {tag}
                            </span>
                          ))}
                          {video.tags.length > 3 && (
                            <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">
                              +{video.tags.length - 3} more
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    
                    {/* Video Number */}
                    <div className="flex-shrink-0 ml-4">
                      <span className="text-2xl font-bold text-gray-300">
                        {String(index + 1).padStart(2, '0')}
                      </span>
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  {video.progress && (
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                        <span>
                          {video.progress.is_completed 
                            ? 'Completed' 
                            : `${Math.round(video.progress.completion_percentage)}% watched`
                          }
                        </span>
                        {video.progress.last_watched_at && (
                          <span className="text-xs">
                            Last watched: {new Date(video.progress.last_watched_at).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                      
                      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full transition-all duration-300 ${
                            video.progress.is_completed 
                              ? 'bg-green-500' 
                              : 'bg-blue-500'
                          }`}
                          style={{ width: `${video.progress.completion_percentage}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State for Filtered Results */}
      {filteredVideos.length === 0 && filter !== 'all' && (
        <div className="text-center py-8">
          <Eye className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">
            No {filter.replace('-', ' ')} videos found
          </p>
          <button
            onClick={() => setFilter('all')}
            className="mt-2 text-blue-600 hover:text-blue-800"
          >
            View all videos
          </button>
        </div>
      )}
    </div>
  );
};

export default VideoList;

