import React, { useState, useEffect, useCallback } from 'react';
import { Search, Filter, X, Clock, Download, Star, BookOpen, Play, FileText } from 'lucide-react';
import { debounce } from 'lodash';
import apiService from '../../services/api';

const SearchInterface = ({ onResultSelect, initialQuery = '', contentType = 'all' }) => {
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  const [pagination, setPagination] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  
  // Filter states
  const [filters, setFilters] = useState({
    type: contentType, // all, videos, knowledge, courses
    category: '',
    difficulty: '',
    format: '',
    tags: [],
    dateRange: '',
    sortBy: 'relevance', // relevance, date, popularity, rating
    sortOrder: 'desc'
  });
  
  const [categories, setCategories] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [recentSearches, setRecentSearches] = useState([]);

  useEffect(() => {
    loadCategories();
    loadRecentSearches();
  }, []);

  useEffect(() => {
    if (query.trim()) {
      debouncedSearch(query, filters, currentPage);
    } else {
      setResults([]);
      setPagination(null);
    }
  }, [query, filters, currentPage]);

  const loadCategories = async () => {
    try {
      const response = await apiService.get('/knowledge/categories');
      setCategories(response.categories || []);
    } catch (err) {
      console.error('Error loading categories:', err);
    }
  };

  const loadRecentSearches = () => {
    const recent = JSON.parse(localStorage.getItem('qryti_recent_searches') || '[]');
    setRecentSearches(recent.slice(0, 5));
  };

  const saveRecentSearch = (searchQuery) => {
    if (!searchQuery.trim()) return;
    
    const recent = JSON.parse(localStorage.getItem('qryti_recent_searches') || '[]');
    const updated = [searchQuery, ...recent.filter(s => s !== searchQuery)].slice(0, 10);
    localStorage.setItem('qryti_recent_searches', JSON.stringify(updated));
    setRecentSearches(updated.slice(0, 5));
  };

  const performSearch = async (searchQuery, searchFilters, page = 1) => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        q: searchQuery,
        page: page.toString(),
        per_page: '20',
        sort: searchFilters.sortBy,
        order: searchFilters.sortOrder
      });

      // Add filters
      if (searchFilters.category) params.append('category_id', searchFilters.category);
      if (searchFilters.difficulty) params.append('difficulty', searchFilters.difficulty);
      if (searchFilters.format) params.append('format', searchFilters.format);
      if (searchFilters.dateRange) params.append('date_range', searchFilters.dateRange);
      if (searchFilters.tags.length > 0) params.append('tags', searchFilters.tags.join(','));

      let searchResults = [];
      let searchPagination = null;

      // Search different content types based on filter
      if (searchFilters.type === 'all' || searchFilters.type === 'knowledge') {
        const knowledgeResponse = await apiService.get(`/knowledge/search?${params.toString()}`);
        const knowledgeResults = (knowledgeResponse.results || []).map(item => ({
          ...item,
          content_type: 'knowledge',
          icon: getContentIcon('knowledge', item.resource_type),
          url: `/knowledge/${item.id}`,
          subtitle: item.description,
          metadata: {
            author: item.author,
            downloads: item.download_count,
            rating: item.average_rating,
            format: item.file_format
          }
        }));
        searchResults = [...searchResults, ...knowledgeResults];
        if (!searchPagination) searchPagination = knowledgeResponse.pagination;
      }

      if (searchFilters.type === 'all' || searchFilters.type === 'videos') {
        const videoParams = new URLSearchParams(params);
        videoParams.delete('format'); // Videos don't have file formats
        
        const videoResponse = await apiService.get(`/videos/search?${videoParams.toString()}`);
        const videoResults = (videoResponse.results || []).map(item => ({
          ...item,
          content_type: 'video',
          icon: getContentIcon('video', item.video_type),
          url: `/videos/${item.id}`,
          subtitle: item.description,
          metadata: {
            duration: item.duration_formatted,
            views: item.view_count,
            difficulty: item.difficulty_level,
            type: item.video_type
          }
        }));
        searchResults = [...searchResults, ...videoResults];
        if (!searchPagination) searchPagination = videoResponse.pagination;
      }

      if (searchFilters.type === 'all' || searchFilters.type === 'courses') {
        const courseResponse = await apiService.get(`/courses/search?${params.toString()}`);
        const courseResults = (courseResponse.results || []).map(item => ({
          ...item,
          content_type: 'course',
          icon: getContentIcon('course'),
          url: `/courses/${item.id}`,
          subtitle: item.description,
          metadata: {
            modules: item.module_count,
            duration: item.estimated_duration,
            level: item.difficulty_level,
            enrolled: item.enrollment_count
          }
        }));
        searchResults = [...searchResults, ...courseResults];
        if (!searchPagination) searchPagination = courseResponse.pagination;
      }

      // Sort combined results by relevance/date
      if (searchFilters.type === 'all') {
        searchResults.sort((a, b) => {
          if (searchFilters.sortBy === 'date') {
            const dateA = new Date(a.created_at || a.published_at);
            const dateB = new Date(b.created_at || b.published_at);
            return searchFilters.sortOrder === 'desc' ? dateB - dateA : dateA - dateB;
          }
          // Default relevance sorting (can be enhanced with scoring)
          return 0;
        });
      }

      setResults(searchResults);
      setPagination(searchPagination);
      saveRecentSearch(searchQuery);

    } catch (err) {
      setError('Search failed. Please try again.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const debouncedSearch = useCallback(
    debounce((searchQuery, searchFilters, page) => {
      performSearch(searchQuery, searchFilters, page);
    }, 300),
    []
  );

  const getContentIcon = (contentType, subType = '') => {
    switch (contentType) {
      case 'video':
        return <Play className="w-4 h-4" />;
      case 'knowledge':
        return subType === 'template' ? <FileText className="w-4 h-4" /> : <Download className="w-4 h-4" />;
      case 'course':
        return <BookOpen className="w-4 h-4" />;
      default:
        return <Search className="w-4 h-4" />;
    }
  };

  const getContentTypeColor = (contentType) => {
    switch (contentType) {
      case 'video':
        return 'bg-red-100 text-red-800';
      case 'knowledge':
        return 'bg-blue-100 text-blue-800';
      case 'course':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleFilterChange = (filterKey, value) => {
    setFilters(prev => ({
      ...prev,
      [filterKey]: value
    }));
    setCurrentPage(1);
  };

  const handleTagAdd = (tag) => {
    if (!filters.tags.includes(tag)) {
      setFilters(prev => ({
        ...prev,
        tags: [...prev.tags, tag]
      }));
    }
  };

  const handleTagRemove = (tag) => {
    setFilters(prev => ({
      ...prev,
      tags: prev.tags.filter(t => t !== tag)
    }));
  };

  const clearFilters = () => {
    setFilters({
      type: 'all',
      category: '',
      difficulty: '',
      format: '',
      tags: [],
      dateRange: '',
      sortBy: 'relevance',
      sortOrder: 'desc'
    });
    setCurrentPage(1);
  };

  const handleResultClick = (result) => {
    if (onResultSelect) {
      onResultSelect(result);
    } else {
      // Default navigation
      window.location.href = result.url;
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Search Input */}
      <div className="relative mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search videos, resources, courses..."
            className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
          />
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`absolute right-3 top-1/2 transform -translate-y-1/2 p-1 rounded ${
              showFilters ? 'text-blue-600 bg-blue-50' : 'text-gray-400 hover:text-gray-600'
            }`}
          >
            <Filter className="w-5 h-5" />
          </button>
        </div>

        {/* Recent Searches */}
        {!query && recentSearches.length > 0 && (
          <div className="absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-lg shadow-lg mt-1 z-10">
            <div className="p-3 border-b border-gray-100">
              <div className="flex items-center text-sm text-gray-600">
                <Clock className="w-4 h-4 mr-2" />
                Recent Searches
              </div>
            </div>
            <div className="py-2">
              {recentSearches.map((search, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(search)}
                  className="w-full text-left px-3 py-2 hover:bg-gray-50 text-sm"
                >
                  {search}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Content Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Content Type
              </label>
              <select
                value={filters.type}
                onChange={(e) => handleFilterChange('type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Content</option>
                <option value="videos">Videos</option>
                <option value="knowledge">Knowledge Base</option>
                <option value="courses">Courses</option>
              </select>
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category
              </label>
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Categories</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Difficulty */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Difficulty
              </label>
              <select
                value={filters.difficulty}
                onChange={(e) => handleFilterChange('difficulty', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Any Level</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
                <option value="expert">Expert</option>
              </select>
            </div>

            {/* Sort By */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sort By
              </label>
              <select
                value={filters.sortBy}
                onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="relevance">Relevance</option>
                <option value="date">Date</option>
                <option value="popularity">Popularity</option>
                <option value="rating">Rating</option>
              </select>
            </div>
          </div>

          {/* Tags */}
          {filters.tags.length > 0 && (
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Active Tags
              </label>
              <div className="flex flex-wrap gap-2">
                {filters.tags.map(tag => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                  >
                    {tag}
                    <button
                      onClick={() => handleTagRemove(tag)}
                      className="ml-2 text-blue-600 hover:text-blue-800"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Clear Filters */}
          <div className="mt-4 flex justify-end">
            <button
              onClick={clearFilters}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
            >
              Clear All Filters
            </button>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-2">Searching...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Results */}
      {!loading && results.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-gray-600">
              {pagination?.total || results.length} results found
              {query && ` for "${query}"`}
            </p>
          </div>

          {results.map((result, index) => (
            <div
              key={`${result.content_type}-${result.id}-${index}`}
              onClick={() => handleResultClick(result)}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
            >
              <div className="flex items-start space-x-4">
                {/* Content Icon */}
                <div className="flex-shrink-0 mt-1">
                  {result.icon}
                </div>

                {/* Content Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600">
                        {result.title}
                      </h3>
                      
                      <div className="flex items-center space-x-2 mt-1">
                        <span className={`px-2 py-1 text-xs rounded-full ${getContentTypeColor(result.content_type)}`}>
                          {result.content_type}
                        </span>
                        
                        {result.metadata?.rating && (
                          <div className="flex items-center">
                            <Star className="w-4 h-4 text-yellow-400 fill-current" />
                            <span className="text-sm text-gray-600 ml-1">
                              {result.metadata.rating}
                            </span>
                          </div>
                        )}
                      </div>

                      {result.subtitle && (
                        <p className="text-gray-600 mt-2 line-clamp-2">
                          {result.subtitle}
                        </p>
                      )}

                      {/* Metadata */}
                      <div className="flex items-center space-x-4 mt-3 text-sm text-gray-500">
                        {result.metadata?.author && (
                          <span>By {result.metadata.author}</span>
                        )}
                        {result.metadata?.duration && (
                          <span>{result.metadata.duration}</span>
                        )}
                        {result.metadata?.downloads && (
                          <span>{result.metadata.downloads} downloads</span>
                        )}
                        {result.metadata?.format && (
                          <span className="uppercase">{result.metadata.format}</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Pagination */}
          {pagination && pagination.pages > 1 && (
            <div className="flex items-center justify-center space-x-2 mt-8">
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={!pagination.has_prev}
                className="px-3 py-2 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Previous
              </button>
              
              <span className="px-4 py-2 text-gray-600">
                Page {pagination.page} of {pagination.pages}
              </span>
              
              <button
                onClick={() => setCurrentPage(prev => Math.min(pagination.pages, prev + 1))}
                disabled={!pagination.has_next}
                className="px-3 py-2 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}

      {/* No Results */}
      {!loading && query && results.length === 0 && (
        <div className="text-center py-8">
          <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No results found
          </h3>
          <p className="text-gray-600 mb-4">
            Try adjusting your search terms or filters
          </p>
          <button
            onClick={clearFilters}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Clear Filters
          </button>
        </div>
      )}
    </div>
  );
};

export default SearchInterface;

