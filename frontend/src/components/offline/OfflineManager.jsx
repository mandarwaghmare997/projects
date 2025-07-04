import React, { useState, useEffect } from 'react';
import { 
  Download, Trash2, RefreshCw, Wifi, WifiOff, HardDrive, 
  CheckCircle, AlertCircle, Clock, Play, FileText, Pause
} from 'lucide-react';
import apiService from '../../services/api';

const OfflineManager = () => {
  const [offlineContent, setOfflineContent] = useState([]);
  const [downloadQueue, setDownloadQueue] = useState([]);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [storageInfo, setStorageInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(new Set());

  useEffect(() => {
    loadOfflineContent();
    loadStorageInfo();
    
    // Listen for online/offline events
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const loadOfflineContent = async () => {
    try {
      setLoading(true);
      
      // Load offline content from localStorage/IndexedDB
      const offlineData = JSON.parse(localStorage.getItem('qryti_offline_content') || '[]');
      setOfflineContent(offlineData);
      
      // Load download queue
      const queueData = JSON.parse(localStorage.getItem('qryti_download_queue') || '[]');
      setDownloadQueue(queueData);
      
    } catch (err) {
      console.error('Error loading offline content:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadStorageInfo = async () => {
    try {
      if ('storage' in navigator && 'estimate' in navigator.storage) {
        const estimate = await navigator.storage.estimate();
        setStorageInfo({
          used: estimate.usage || 0,
          available: estimate.quota || 0,
          usedFormatted: formatBytes(estimate.usage || 0),
          availableFormatted: formatBytes(estimate.quota || 0)
        });
      }
    } catch (err) {
      console.error('Error getting storage info:', err);
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const downloadForOffline = async (content) => {
    if (downloading.has(content.id)) return;
    
    setDownloading(prev => new Set([...prev, content.id]));
    
    try {
      let downloadData = null;
      
      if (content.content_type === 'video') {
        // For videos, we'll store metadata and transcript
        // In a real app, you might download video segments
        const response = await apiService.get(`/videos/${content.id}/offline-data`);
        downloadData = {
          ...content,
          offline_data: response,
          downloaded_at: new Date().toISOString(),
          size: response.estimated_size || 0
        };
      } else if (content.content_type === 'knowledge') {
        // For knowledge resources, download the actual file
        const response = await apiService.get(`/knowledge/resources/${content.id}/download`, {
          responseType: 'blob'
        });
        
        // Store file in IndexedDB (simplified here)
        downloadData = {
          ...content,
          offline_data: {
            blob: response,
            url: URL.createObjectURL(response)
          },
          downloaded_at: new Date().toISOString(),
          size: response.size || 0
        };
      }
      
      // Add to offline content
      const updatedOfflineContent = [...offlineContent, downloadData];
      setOfflineContent(updatedOfflineContent);
      localStorage.setItem('qryti_offline_content', JSON.stringify(updatedOfflineContent));
      
      // Remove from download queue if it was there
      const updatedQueue = downloadQueue.filter(item => 
        !(item.id === content.id && item.content_type === content.content_type)
      );
      setDownloadQueue(updatedQueue);
      localStorage.setItem('qryti_download_queue', JSON.stringify(updatedQueue));
      
      // Update storage info
      await loadStorageInfo();
      
    } catch (err) {
      console.error('Download failed:', err);
      alert('Download failed. Please try again.');
    } finally {
      setDownloading(prev => {
        const newSet = new Set(prev);
        newSet.delete(content.id);
        return newSet;
      });
    }
  };

  const removeOfflineContent = async (content) => {
    try {
      // Clean up blob URLs
      if (content.offline_data?.url) {
        URL.revokeObjectURL(content.offline_data.url);
      }
      
      // Remove from offline content
      const updatedContent = offlineContent.filter(item => 
        !(item.id === content.id && item.content_type === content.content_type)
      );
      setOfflineContent(updatedContent);
      localStorage.setItem('qryti_offline_content', JSON.stringify(updatedContent));
      
      // Update storage info
      await loadStorageInfo();
      
    } catch (err) {
      console.error('Error removing offline content:', err);
    }
  };

  const addToDownloadQueue = (content) => {
    const queueItem = {
      ...content,
      queued_at: new Date().toISOString()
    };
    
    const updatedQueue = [...downloadQueue, queueItem];
    setDownloadQueue(updatedQueue);
    localStorage.setItem('qryti_download_queue', JSON.stringify(updatedQueue));
  };

  const removeFromQueue = (content) => {
    const updatedQueue = downloadQueue.filter(item => 
      !(item.id === content.id && item.content_type === content.content_type)
    );
    setDownloadQueue(updatedQueue);
    localStorage.setItem('qryti_download_queue', JSON.stringify(updatedQueue));
  };

  const processDownloadQueue = async () => {
    if (!isOnline || downloadQueue.length === 0) return;
    
    for (const item of downloadQueue) {
      if (!downloading.has(item.id)) {
        await downloadForOffline(item);
        // Add delay between downloads to avoid overwhelming the server
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
  };

  const clearAllOfflineContent = async () => {
    if (confirm('Are you sure you want to remove all offline content?')) {
      // Clean up blob URLs
      offlineContent.forEach(content => {
        if (content.offline_data?.url) {
          URL.revokeObjectURL(content.offline_data.url);
        }
      });
      
      setOfflineContent([]);
      localStorage.removeItem('qryti_offline_content');
      await loadStorageInfo();
    }
  };

  const getContentIcon = (contentType) => {
    switch (contentType) {
      case 'video':
        return <Play className="w-5 h-5 text-red-500" />;
      case 'knowledge':
        return <FileText className="w-5 h-5 text-blue-500" />;
      default:
        return <FileText className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusIcon = (content) => {
    if (downloading.has(content.id)) {
      return <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />;
    }
    
    const isOffline = offlineContent.some(item => 
      item.id === content.id && item.content_type === content.content_type
    );
    
    if (isOffline) {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
    
    const isQueued = downloadQueue.some(item => 
      item.id === content.id && item.content_type === content.content_type
    );
    
    if (isQueued) {
      return <Clock className="w-4 h-4 text-yellow-500" />;
    }
    
    return null;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-300 rounded w-1/3"></div>
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-16 bg-gray-300 rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Offline Content
              </h1>
              <p className="text-gray-600">
                Download content for offline access and manage your local storage
              </p>
            </div>
            
            <div className="flex items-center space-x-2">
              {isOnline ? (
                <div className="flex items-center text-green-600">
                  <Wifi className="w-5 h-5 mr-2" />
                  Online
                </div>
              ) : (
                <div className="flex items-center text-red-600">
                  <WifiOff className="w-5 h-5 mr-2" />
                  Offline
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Storage Info */}
        {storageInfo && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <HardDrive className="w-5 h-5 text-gray-500 mr-2" />
                <h3 className="text-lg font-semibold text-gray-900">
                  Storage Usage
                </h3>
              </div>
              
              <button
                onClick={clearAllOfflineContent}
                disabled={offlineContent.length === 0}
                className="px-3 py-2 text-sm text-red-600 hover:text-red-800 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Clear All
              </button>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Used: {storageInfo.usedFormatted}</span>
                <span>Available: {storageInfo.availableFormatted}</span>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ 
                    width: `${Math.min((storageInfo.used / storageInfo.available) * 100, 100)}%` 
                  }}
                ></div>
              </div>
            </div>
          </div>
        )}

        {/* Download Queue */}
        {downloadQueue.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Download Queue ({downloadQueue.length})
              </h3>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={processDownloadQueue}
                  disabled={!isOnline}
                  className="px-3 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Process Queue
                </button>
              </div>
            </div>
            
            <div className="space-y-2">
              {downloadQueue.map((item, index) => (
                <div key={`${item.id}-${item.content_type}`} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                  <div className="flex items-center space-x-3">
                    {getContentIcon(item.content_type)}
                    <div>
                      <p className="font-medium text-gray-900">{item.title}</p>
                      <p className="text-sm text-gray-500">
                        Queued {new Date(item.queued_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => downloadForOffline(item)}
                      disabled={!isOnline || downloading.has(item.id)}
                      className="p-1 text-blue-600 hover:text-blue-800 disabled:opacity-50"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => removeFromQueue(item)}
                      className="p-1 text-red-600 hover:text-red-800"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Offline Content */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Downloaded Content ({offlineContent.length})
          </h3>
          
          {offlineContent.length > 0 ? (
            <div className="space-y-4">
              {offlineContent.map((content) => (
                <div key={`${content.id}-${content.content_type}`} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center space-x-4">
                    {getContentIcon(content.content_type)}
                    
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{content.title}</h4>
                      <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          content.content_type === 'video' 
                            ? 'bg-red-100 text-red-800' 
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {content.content_type}
                        </span>
                        <span>Downloaded {new Date(content.downloaded_at).toLocaleDateString()}</span>
                        {content.size > 0 && <span>{formatBytes(content.size)}</span>}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <button
                      onClick={() => removeOfflineContent(content)}
                      className="p-2 text-red-600 hover:text-red-800"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Download className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h4 className="text-lg font-semibold text-gray-900 mb-2">
                No offline content
              </h4>
              <p className="text-gray-600">
                Download videos and resources to access them offline
              </p>
            </div>
          )}
        </div>

        {/* Offline Tips */}
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-6 mt-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">
            Offline Access Tips
          </h3>
          <ul className="text-sm text-blue-800 space-y-2">
            <li>• Download content while connected to Wi-Fi to save mobile data</li>
            <li>• Videos are optimized for offline viewing with reduced file sizes</li>
            <li>• Downloaded resources remain available even when offline</li>
            <li>• Progress tracking syncs when you reconnect to the internet</li>
            <li>• Manage storage space by removing content you no longer need</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default OfflineManager;

