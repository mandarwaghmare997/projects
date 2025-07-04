import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, TrendingUp, Clock, Star } from 'lucide-react';
import SearchInterface from '../components/search/SearchInterface';
import apiService from '../services/api';

const SearchPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [trendingSearches, setTrendingSearches] = useState([]);
  const [popularContent, setPopularContent] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  const initialQuery = searchParams.get('q') || '';
  const contentType = searchParams.get('type') || 'all';

  useEffect(() => {
    loadSearchPageData();
  }, []);

  const loadSearchPageData = async () => {
    try {
      setLoading(true);
      
      // Load trending searches, popular content, and recent activity
      const [knowledgeStats, videoStats] = await Promise.all([
        apiService.get('/knowledge/stats'),
        apiService.get('/videos/stats')
      ]);

      // Extract trending/popular data
      if (knowledgeStats.popular_resources) {
        setPopularContent(prev => [...prev, ...knowledgeStats.popular_resources.slice(0, 5)]);
      }

      // Mock trending searches (in real app, this would come from analytics)
      setTrendingSearches([
        'ISO 42001 implementation',
        'AI risk assessment',
        'governance framework',
        'compliance checklist',
        'audit preparation'
      ]);

      // Mock recent activity (in real app, this would be user-specific)
      setRecentActivity([
        { type: 'search', query: 'AI ethics training', timestamp: new Date(Date.now() - 3600000) },
        { type: 'download', title: 'ISO 42001 Standard', timestamp: new Date(Date.now() - 7200000) },
        { type: 'bookmark', title: 'Risk Assessment Template', timestamp: new Date(Date.now() - 10800000) }
      ]);

    } catch (err) {
      console.error('Error loading search page data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleResultSelect = (result) => {
    // Navigate to the appropriate page based on content type
    switch (result.content_type) {
      case 'video':
        navigate(`/videos/${result.id}`);
        break;
      case 'knowledge':
        navigate(`/knowledge/${result.id}`);
        break;
      case 'course':
        navigate(`/courses/${result.id}`);
        break;
      default:
        // Fallback to result URL
        if (result.url) {
          navigate(result.url);
        }
    }
  };

  const handleTrendingClick = (query) => {
    navigate(`/search?q=${encodeURIComponent(query)}`);
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const diff = now - new Date(timestamp);
    const hours = Math.floor(diff / (1000 * 60 * 60));
    
    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center text-blue-600 hover:text-blue-800 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </button>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Search Learning Resources
          </h1>
          <p className="text-gray-600">
            Find videos, documents, courses, and more across the Qryti Learn platform
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Search Area */}
          <div className="lg:col-span-3">
            <SearchInterface
              initialQuery={initialQuery}
              contentType={contentType}
              onResultSelect={handleResultSelect}
            />
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Trending Searches */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center mb-4">
                <TrendingUp className="w-5 h-5 text-orange-500 mr-2" />
                <h3 className="text-lg font-semibold text-gray-900">
                  Trending Searches
                </h3>
              </div>
              
              <div className="space-y-2">
                {trendingSearches.map((query, index) => (
                  <button
                    key={index}
                    onClick={() => handleTrendingClick(query)}
                    className="block w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md transition-colors"
                  >
                    <span className="text-orange-500 font-medium mr-2">
                      #{index + 1}
                    </span>
                    {query}
                  </button>
                ))}
              </div>
            </div>

            {/* Popular Content */}
            {popularContent.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center mb-4">
                  <Star className="w-5 h-5 text-yellow-500 mr-2" />
                  <h3 className="text-lg font-semibold text-gray-900">
                    Popular Content
                  </h3>
                </div>
                
                <div className="space-y-3">
                  {popularContent.map((item, index) => (
                    <div
                      key={index}
                      className="flex items-start space-x-3 p-2 hover:bg-gray-50 rounded-md cursor-pointer"
                      onClick={() => handleResultSelect({
                        ...item,
                        content_type: 'knowledge',
                        url: `/knowledge/${item.id}`
                      })}
                    >
                      <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 text-sm font-medium">
                          {index + 1}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 line-clamp-2">
                          {item.title}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {item.download_count} downloads
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recent Activity */}
            {recentActivity.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center mb-4">
                  <Clock className="w-5 h-5 text-blue-500 mr-2" />
                  <h3 className="text-lg font-semibold text-gray-900">
                    Recent Activity
                  </h3>
                </div>
                
                <div className="space-y-3">
                  {recentActivity.map((activity, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-900">
                          {activity.type === 'search' && `Searched for "${activity.query}"`}
                          {activity.type === 'download' && `Downloaded "${activity.title}"`}
                          {activity.type === 'bookmark' && `Bookmarked "${activity.title}"`}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {formatTimeAgo(activity.timestamp)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Search Tips */}
            <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">
                Search Tips
              </h3>
              <ul className="text-sm text-blue-800 space-y-2">
                <li>• Use quotes for exact phrases: "AI governance"</li>
                <li>• Filter by content type for better results</li>
                <li>• Try different keywords if no results found</li>
                <li>• Use tags to find related content</li>
                <li>• Sort by date to find latest resources</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SearchPage;

