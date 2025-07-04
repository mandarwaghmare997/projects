import React, { useState, useEffect } from 'react';
import { 
  Bookmark, BookmarkCheck, Trash2, Edit3, Tag, Search, 
  Filter, Grid, List, Calendar, Star, Download, Play, FileText,
  FolderPlus, Folder, Plus, X
} from 'lucide-react';
import apiService from '../../services/api';

const BookmarkManager = () => {
  const [bookmarks, setBookmarks] = useState([]);
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('grid');
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [showCreateCollection, setShowCreateCollection] = useState(false);
  const [editingBookmark, setEditingBookmark] = useState(null);
  const [selectedBookmarks, setSelectedBookmarks] = useState(new Set());

  useEffect(() => {
    loadBookmarks();
    loadCollections();
  }, []);

  useEffect(() => {
    filterBookmarks();
  }, [searchQuery, filterType, sortBy, selectedCollection]);

  const loadBookmarks = async () => {
    try {
      setLoading(true);
      
      // Load both video and knowledge bookmarks
      const [videoBookmarks, knowledgeBookmarks] = await Promise.all([
        apiService.get('/videos/my/bookmarks'),
        apiService.get('/knowledge/my/bookmarks')
      ]);

      const allBookmarks = [
        ...(videoBookmarks.bookmarks || []).map(item => ({
          ...item,
          content_type: 'video',
          icon: <Play className="w-5 h-5 text-red-500" />
        })),
        ...(knowledgeBookmarks.bookmarks || []).map(item => ({
          ...item,
          content_type: 'knowledge',
          icon: <FileText className="w-5 h-5 text-blue-500" />
        }))
      ];

      setBookmarks(allBookmarks);
    } catch (err) {
      setError('Failed to load bookmarks');
      console.error('Error loading bookmarks:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadCollections = async () => {
    try {
      const response = await apiService.get('/knowledge/my/collections');
      setCollections(response.collections || []);
    } catch (err) {
      console.error('Error loading collections:', err);
    }
  };

  const filterBookmarks = () => {
    let filtered = [...bookmarks];

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(bookmark => 
        bookmark.title?.toLowerCase().includes(query) ||
        bookmark.description?.toLowerCase().includes(query) ||
        bookmark.bookmark?.notes?.toLowerCase().includes(query)
      );
    }

    // Type filter
    if (filterType !== 'all') {
      filtered = filtered.filter(bookmark => bookmark.content_type === filterType);
    }

    // Collection filter
    if (selectedCollection) {
      // Filter by collection (would need collection membership data)
      // This is a placeholder for collection filtering logic
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'title':
          return a.title?.localeCompare(b.title) || 0;
        case 'created_at':
          return new Date(b.bookmark?.created_at) - new Date(a.bookmark?.created_at);
        case 'updated_at':
          return new Date(b.bookmark?.updated_at) - new Date(a.bookmark?.updated_at);
        default:
          return 0;
      }
    });

    return filtered;
  };

  const handleRemoveBookmark = async (bookmark) => {
    try {
      const endpoint = bookmark.content_type === 'video' 
        ? `/videos/${bookmark.id}/bookmark`
        : `/knowledge/resources/${bookmark.id}/bookmark`;
      
      await apiService.delete(endpoint);
      
      setBookmarks(prev => prev.filter(b => 
        !(b.id === bookmark.id && b.content_type === bookmark.content_type)
      ));
    } catch (err) {
      console.error('Error removing bookmark:', err);
      alert('Failed to remove bookmark');
    }
  };

  const handleEditBookmark = async (bookmark, updates) => {
    try {
      const endpoint = bookmark.content_type === 'video' 
        ? `/videos/${bookmark.id}/bookmark`
        : `/knowledge/resources/${bookmark.id}/bookmark`;
      
      const response = await apiService.post(endpoint, updates);
      
      setBookmarks(prev => prev.map(b => 
        b.id === bookmark.id && b.content_type === bookmark.content_type
          ? { ...b, bookmark: response.bookmark }
          : b
      ));
      
      setEditingBookmark(null);
    } catch (err) {
      console.error('Error updating bookmark:', err);
      alert('Failed to update bookmark');
    }
  };

  const handleCreateCollection = async (collectionData) => {
    try {
      const response = await apiService.post('/knowledge/collections', collectionData);
      setCollections(prev => [...prev, response]);
      setShowCreateCollection(false);
    } catch (err) {
      console.error('Error creating collection:', err);
      alert('Failed to create collection');
    }
  };

  const handleBulkAction = async (action) => {
    if (selectedBookmarks.size === 0) return;

    try {
      switch (action) {
        case 'remove':
          for (const bookmarkKey of selectedBookmarks) {
            const [id, type] = bookmarkKey.split('-');
            const bookmark = bookmarks.find(b => b.id.toString() === id && b.content_type === type);
            if (bookmark) {
              await handleRemoveBookmark(bookmark);
            }
          }
          setSelectedBookmarks(new Set());
          break;
        case 'add_to_collection':
          // Implement add to collection logic
          break;
        default:
          break;
      }
    } catch (err) {
      console.error('Error performing bulk action:', err);
    }
  };

  const toggleBookmarkSelection = (bookmark) => {
    const key = `${bookmark.id}-${bookmark.content_type}`;
    const newSelected = new Set(selectedBookmarks);
    
    if (newSelected.has(key)) {
      newSelected.delete(key);
    } else {
      newSelected.add(key);
    }
    
    setSelectedBookmarks(newSelected);
  };

  const filteredBookmarks = filterBookmarks();

  const BookmarkCard = ({ bookmark }) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={selectedBookmarks.has(`${bookmark.id}-${bookmark.content_type}`)}
              onChange={() => toggleBookmarkSelection(bookmark)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            {bookmark.icon}
            <span className={`px-2 py-1 text-xs rounded-full ${
              bookmark.content_type === 'video' 
                ? 'bg-red-100 text-red-800' 
                : 'bg-blue-100 text-blue-800'
            }`}>
              {bookmark.content_type}
            </span>
          </div>
          
          <div className="flex items-center space-x-1">
            <button
              onClick={() => setEditingBookmark(bookmark)}
              className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
            >
              <Edit3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleRemoveBookmark(bookmark)}
              className="p-1 text-gray-400 hover:text-red-600 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
          {bookmark.title}
        </h3>
        
        {bookmark.description && (
          <p className="text-gray-600 text-sm mb-3 line-clamp-2">
            {bookmark.description}
          </p>
        )}

        {/* Bookmark Notes */}
        {bookmark.bookmark?.notes && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3 mb-3">
            <p className="text-sm text-gray-700">
              <strong>Notes:</strong> {bookmark.bookmark.notes}
            </p>
          </div>
        )}

        {/* Tags */}
        {bookmark.bookmark?.tags && bookmark.bookmark.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {bookmark.bookmark.tags.map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Metadata */}
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center">
            <Calendar className="w-4 h-4 mr-1" />
            {new Date(bookmark.bookmark?.created_at).toLocaleDateString()}
          </div>
          
          {bookmark.average_rating && (
            <div className="flex items-center">
              <Star className="w-4 h-4 mr-1 text-yellow-400 fill-current" />
              {bookmark.average_rating}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const BookmarkListItem = ({ bookmark }) => (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow">
      <div className="flex items-center space-x-4">
        <input
          type="checkbox"
          checked={selectedBookmarks.has(`${bookmark.id}-${bookmark.content_type}`)}
          onChange={() => toggleBookmarkSelection(bookmark)}
          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        
        <div className="flex-shrink-0">
          {bookmark.icon}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 truncate">
                {bookmark.title}
              </h3>
              
              <div className="flex items-center space-x-2 mt-1">
                <span className={`px-2 py-1 text-xs rounded-full ${
                  bookmark.content_type === 'video' 
                    ? 'bg-red-100 text-red-800' 
                    : 'bg-blue-100 text-blue-800'
                }`}>
                  {bookmark.content_type}
                </span>
                
                {bookmark.bookmark?.notes && (
                  <span className="text-sm text-gray-600">
                    "{bookmark.bookmark.notes}"
                  </span>
                )}
              </div>
              
              <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                <span>
                  Bookmarked {new Date(bookmark.bookmark?.created_at).toLocaleDateString()}
                </span>
                {bookmark.average_rating && (
                  <div className="flex items-center">
                    <Star className="w-4 h-4 mr-1 text-yellow-400 fill-current" />
                    {bookmark.average_rating}
                  </div>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-2 ml-4">
              <button
                onClick={() => setEditingBookmark(bookmark)}
                className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
              >
                <Edit3 className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleRemoveBookmark(bookmark)}
                className="p-2 text-gray-400 hover:text-red-600 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
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
                <div key={i} className="h-48 bg-gray-300 rounded-lg"></div>
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            My Bookmarks
          </h1>
          <p className="text-gray-600">
            Manage your saved videos, resources, and learning materials
          </p>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            {/* Search and Filters */}
            <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search bookmarks..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Type Filter */}
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Types</option>
                <option value="video">Videos</option>
                <option value="knowledge">Resources</option>
              </select>

              {/* Sort */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="created_at">Date Added</option>
                <option value="updated_at">Last Updated</option>
                <option value="title">Title</option>
              </select>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-4">
              {/* Bulk Actions */}
              {selectedBookmarks.size > 0 && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">
                    {selectedBookmarks.size} selected
                  </span>
                  <button
                    onClick={() => handleBulkAction('remove')}
                    className="px-3 py-1 bg-red-600 text-white text-sm rounded-md hover:bg-red-700"
                  >
                    Remove
                  </button>
                </div>
              )}

              {/* Create Collection */}
              <button
                onClick={() => setShowCreateCollection(true)}
                className="flex items-center px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                <FolderPlus className="w-4 h-4 mr-2" />
                New Collection
              </button>

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

        {/* Collections */}
        {collections.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">
              Collections
            </h2>
            <div className="flex space-x-2 overflow-x-auto pb-2">
              <button
                onClick={() => setSelectedCollection(null)}
                className={`flex items-center px-3 py-2 rounded-md whitespace-nowrap ${
                  selectedCollection === null
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Bookmark className="w-4 h-4 mr-2" />
                All Bookmarks
              </button>
              {collections.map(collection => (
                <button
                  key={collection.id}
                  onClick={() => setSelectedCollection(collection.id)}
                  className={`flex items-center px-3 py-2 rounded-md whitespace-nowrap ${
                    selectedCollection === collection.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Folder className="w-4 h-4 mr-2" />
                  {collection.name}
                  <span className="ml-2 px-2 py-0.5 bg-gray-200 text-gray-600 text-xs rounded-full">
                    {collection.resource_count}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Bookmarks */}
        {filteredBookmarks.length > 0 ? (
          <div className={
            viewMode === 'grid' 
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
              : 'space-y-4'
          }>
            {filteredBookmarks.map(bookmark => 
              viewMode === 'grid' ? (
                <BookmarkCard key={`${bookmark.id}-${bookmark.content_type}`} bookmark={bookmark} />
              ) : (
                <BookmarkListItem key={`${bookmark.id}-${bookmark.content_type}`} bookmark={bookmark} />
              )
            )}
          </div>
        ) : (
          <div className="text-center py-12">
            <Bookmark className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No bookmarks found
            </h3>
            <p className="text-gray-600">
              {searchQuery || filterType !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : 'Start bookmarking content to see it here'
              }
            </p>
          </div>
        )}

        {/* Edit Bookmark Modal */}
        {editingBookmark && (
          <EditBookmarkModal
            bookmark={editingBookmark}
            onSave={handleEditBookmark}
            onClose={() => setEditingBookmark(null)}
          />
        )}

        {/* Create Collection Modal */}
        {showCreateCollection && (
          <CreateCollectionModal
            onSave={handleCreateCollection}
            onClose={() => setShowCreateCollection(false)}
          />
        )}
      </div>
    </div>
  );
};

// Edit Bookmark Modal Component
const EditBookmarkModal = ({ bookmark, onSave, onClose }) => {
  const [notes, setNotes] = useState(bookmark.bookmark?.notes || '');
  const [tags, setTags] = useState(bookmark.bookmark?.tags || []);
  const [newTag, setNewTag] = useState('');

  const handleAddTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      setTags([...tags, newTag.trim()]);
      setNewTag('');
    }
  };

  const handleRemoveTag = (tagToRemove) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleSave = () => {
    onSave(bookmark, { notes, tags });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">
          Edit Bookmark
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="3"
              placeholder="Add your notes..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tags
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Add tag..."
              />
              <button
                onClick={handleAddTag}
                className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {tags.map((tag, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                >
                  {tag}
                  <button
                    onClick={() => handleRemoveTag(tag)}
                    className="ml-1 text-blue-600 hover:text-blue-800"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="flex justify-end space-x-3 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};

// Create Collection Modal Component
const CreateCollectionModal = ({ onSave, onClose }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState(false);

  const handleSave = () => {
    if (name.trim()) {
      onSave({
        name: name.trim(),
        description: description.trim(),
        is_public: isPublic
      });
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">
          Create New Collection
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Collection Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter collection name..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="3"
              placeholder="Optional description..."
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="isPublic"
              checked={isPublic}
              onChange={(e) => setIsPublic(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="isPublic" className="ml-2 text-sm text-gray-700">
              Make this collection public
            </label>
          </div>
        </div>

        <div className="flex justify-end space-x-3 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!name.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Create Collection
          </button>
        </div>
      </div>
    </div>
  );
};

export default BookmarkManager;

