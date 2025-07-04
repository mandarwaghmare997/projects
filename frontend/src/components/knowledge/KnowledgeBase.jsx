import React, { useState, useEffect } from 'react';
import { 
  Download, BookOpen, Star, Eye, Calendar, User, Tag, 
  Filter, Grid, List, Search, Bookmark, BookmarkCheck,
  FileText, File, Archive, Video, Book
} from 'lucide-react';
import apiService from '../../services/api';

const KnowledgeBase = () => {
  const [resources, setResources] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // grid, list
  const [sortBy, setSortBy] = useState('title');
  const [filterType, setFilterType] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [pagination, setPagination] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [featuredResources, setFeaturedResources] = useState([]);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadResources();
  }, [selectedCategory, sortBy, filterType, searchQuery, currentPage]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      
      // Load categories, stats, and featured resources in parallel
      const [categoriesResponse, statsResponse, featuredResponse] = await Promise.all([
        apiService.get('/knowledge/categories'),
        apiService.get('/knowledge/stats'),
        apiService.get('/knowledge/resources?featured=true&per_page=6')
      ]);

      setCategories(categoriesResponse.categories || []);
      setStats(statsResponse);
      setFeaturedResources(featuredResponse.resources || []);
      
    } catch (err) {
      setError('Failed to load knowledge base data');
      console.error('Error loading initial data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadResources = async () => {
    try {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        per_page: '12',
        sort: sortBy,
        order: 'desc'
      });

      if (selectedCategory) params.append('category_id', selectedCategory.toString());
      if (filterType !== 'all') params.append('type', filterType);
      if (searchQuery.trim()) params.append('search', searchQuery.trim());

      const response = await apiService.get(`/knowledge/resources?${params.toString()}`);
      setResources(response.resources || []);
      setPagination(response.pagination);
      
    } catch (err) {
      setError('Failed to load resources');
      console.error('Error loading resources:', err);
    }
  };

  const handleResourceDownload = async (resource) => {
    try {
      const response = await apiService.post(`/knowledge/resources/${resource.id}/download`, {}, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${resource.title}.${resource.file_extension}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      // Update download count locally
      setResources(prev => prev.map(r => 
        r.id === resource.id 
          ? { ...r, download_count: r.download_count + 1 }
          : r
      ));
      
    } catch (err) {
      console.error('Download failed:', err);
      alert('Download failed. Please try again.');
    }
  };

  const handleBookmarkToggle = async (resource) => {
    try {
      const response = await apiService.post(`/knowledge/resources/${resource.id}/bookmark`);
      
      // Update bookmark status locally
      setResources(prev => prev.map(r => 
        r.id === resource.id 
          ? { ...r, is_bookmarked: response.bookmark ? true : false }
          : r
      ));
      
    } catch (err) {
      console.error('Bookmark toggle failed:', err);
    }
  };

  const getResourceIcon = (resourceType, fileFormat) => {
    switch (resourceType) {
      case 'template':
        return <FileText className="w-6 h-6 text-blue-500" />;
      case 'guide':
        return <BookOpen className="w-6 h-6 text-green-500" />;
      case 'standard':
        return <File className="w-6 h-6 text-purple-500" />;
      case 'toolkit':
        return <Archive className="w-6 h-6 text-orange-500" />;
      case 'training':
        return <Video className="w-6 h-6 text-red-500" />;
      case 'case_study':
        return <Book className="w-6 h-6 text-indigo-500" />;
      default:
        return <FileText className="w-6 h-6 text-gray-500" />;
    }
  };

  const getFileFormatColor = (format) => {
    switch (format?.toLowerCase()) {
      case 'pdf':
        return 'bg-red-100 text-red-800';
      case 'docx':
      case 'doc':
        return 'bg-blue-100 text-blue-800';
      case 'xlsx':
      case 'xls':
        return 'bg-green-100 text-green-800';
      case 'pptx':
      case 'ppt':
        return 'bg-orange-100 text-orange-800';
      case 'zip':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const ResourceCard = ({ resource }) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            {getResourceIcon(resource.resource_type, resource.file_format)}
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                {resource.title}
              </h3>
              <div className="flex items-center space-x-2 mt-1">
                <span className={`px-2 py-1 text-xs rounded-full ${getFileFormatColor(resource.file_format)}`}>
                  {resource.file_format?.toUpperCase()}
                </span>
                <span className="text-sm text-gray-500">
                  {resource.file_size_formatted}
                </span>
              </div>
            </div>
          </div>
          
          <button
            onClick={() => handleBookmarkToggle(resource)}
            className="text-gray-400 hover:text-yellow-500 transition-colors"
          >
            {resource.is_bookmarked ? (
              <BookmarkCheck className="w-5 h-5 text-yellow-500" />
            ) : (
              <Bookmark className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Description */}
        <p className="text-gray-600 text-sm mb-4 line-clamp-3">
          {resource.description}
        </p>

        {/* Metadata */}
        <div className="space-y-2 mb-4">
          {resource.author && (
            <div className="flex items-center text-sm text-gray-500">
              <User className="w-4 h-4 mr-2" />
              {resource.author}
            </div>
          )}
          
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center">
              <Download className="w-4 h-4 mr-1" />
              {resource.download_count} downloads
            </div>
            
            {resource.average_rating > 0 && (
              <div className="flex items-center">
                <Star className="w-4 h-4 mr-1 text-yellow-400 fill-current" />
                {resource.average_rating} ({resource.rating_count})
              </div>
            )}
          </div>
        </div>

        {/* Tags */}
        {resource.tags && resource.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-4">
            {resource.tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
              >
                {tag}
              </span>
            ))}
            {resource.tags.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                +{resource.tags.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => handleResourceDownload(resource)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <Download className="w-4 h-4 mr-2" />
            Download
          </button>
          
          <div className="flex items-center text-sm text-gray-500">
            <Calendar className="w-4 h-4 mr-1" />
            {new Date(resource.created_at).toLocaleDateString()}
          </div>
        </div>
      </div>
    </div>
  );

  const ResourceListItem = ({ resource }) => (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow">
      <div className="flex items-center space-x-4">
        {/* Icon */}
        <div className="flex-shrink-0">
          {getResourceIcon(resource.resource_type, resource.file_format)}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 truncate">
                {resource.title}
              </h3>
              <p className="text-gray-600 text-sm mt-1 line-clamp-2">
                {resource.description}
              </p>
              
              <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                <span className={`px-2 py-1 text-xs rounded-full ${getFileFormatColor(resource.file_format)}`}>
                  {resource.file_format?.toUpperCase()}
                </span>
                <span>{resource.file_size_formatted}</span>
                {resource.author && <span>By {resource.author}</span>}
                <span>{resource.download_count} downloads</span>
                {resource.average_rating > 0 && (
                  <div className="flex items-center">
                    <Star className="w-4 h-4 mr-1 text-yellow-400 fill-current" />
                    {resource.average_rating}
                  </div>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-2 ml-4">
              <button
                onClick={() => handleBookmarkToggle(resource)}
                className="text-gray-400 hover:text-yellow-500 transition-colors"
              >
                {resource.is_bookmarked ? (
                  <BookmarkCheck className="w-5 h-5 text-yellow-500" />
                ) : (
                  <Bookmark className="w-5 h-5" />
                )}
              </button>
              
              <button
                onClick={() => handleResourceDownload(resource)}
                className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                <Download className="w-4 h-4 mr-1" />
                Download
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-300 rounded w-1/3"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-64 bg-gray-300 rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Knowledge Base
          </h1>
          <p className="text-gray-600 mb-6">
            Comprehensive collection of resources, templates, and guides for AI management systems
          </p>

          {/* Stats */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="text-2xl font-bold text-blue-600">{stats.total_resources}</div>
                <div className="text-sm text-gray-600">Total Resources</div>
              </div>
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="text-2xl font-bold text-green-600">{stats.total_downloads}</div>
                <div className="text-sm text-gray-600">Downloads</div>
              </div>
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="text-2xl font-bold text-purple-600">{stats.total_categories}</div>
                <div className="text-sm text-gray-600">Categories</div>
              </div>
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="text-2xl font-bold text-orange-600">
                  {stats.resource_types?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Resource Types</div>
              </div>
            </div>
          )}
        </div>

        {/* Featured Resources */}
        {featuredResources.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Featured Resources
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {featuredResources.map(resource => (
                <ResourceCard key={resource.id} resource={resource} />
              ))}
            </div>
          </div>
        )}

        {/* Filters and Controls */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            {/* Search */}
            <div className="flex-1 max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search resources..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Controls */}
            <div className="flex items-center space-x-4">
              {/* Category Filter */}
              <select
                value={selectedCategory || ''}
                onChange={(e) => setSelectedCategory(e.target.value ? parseInt(e.target.value) : null)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Categories</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>

              {/* Type Filter */}
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Types</option>
                <option value="template">Templates</option>
                <option value="guide">Guides</option>
                <option value="standard">Standards</option>
                <option value="checklist">Checklists</option>
                <option value="case_study">Case Studies</option>
                <option value="training">Training</option>
              </select>

              {/* Sort */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="title">Title</option>
                <option value="created_at">Date</option>
                <option value="download_count">Downloads</option>
                <option value="rating">Rating</option>
              </select>

              {/* View Mode */}
              <div className="flex border border-gray-300 rounded-md">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-gray-800'}`}
                >
                  <Grid className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-gray-800'}`}
                >
                  <List className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Resources Grid/List */}
        {resources.length > 0 ? (
          <div className={
            viewMode === 'grid' 
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
              : 'space-y-4'
          }>
            {resources.map(resource => 
              viewMode === 'grid' ? (
                <ResourceCard key={resource.id} resource={resource} />
              ) : (
                <ResourceListItem key={resource.id} resource={resource} />
              )
            )}
          </div>
        ) : (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No resources found
            </h3>
            <p className="text-gray-600">
              Try adjusting your search or filter criteria
            </p>
          </div>
        )}

        {/* Pagination */}
        {pagination && pagination.pages > 1 && (
          <div className="flex items-center justify-center space-x-2 mt-8">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={!pagination.has_prev}
              className="px-4 py-2 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Previous
            </button>
            
            <span className="px-4 py-2 text-gray-600">
              Page {pagination.page} of {pagination.pages}
            </span>
            
            <button
              onClick={() => setCurrentPage(prev => Math.min(pagination.pages, prev + 1))}
              disabled={!pagination.has_next}
              className="px-4 py-2 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default KnowledgeBase;

