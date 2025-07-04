import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize, Bookmark, BookmarkCheck, Settings } from 'lucide-react';

const VideoPlayer = ({ 
  video, 
  onProgressUpdate, 
  onBookmarkToggle,
  autoplay = false,
  showControls = true 
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showBookmarkForm, setShowBookmarkForm] = useState(false);
  const [quality, setQuality] = useState('720p');
  
  const playerRef = useRef(null);
  const progressUpdateInterval = useRef(null);
  const lastProgressUpdate = useRef(0);

  // YouTube Player API integration
  useEffect(() => {
    if (!video?.youtube_id) return;

    // Load YouTube IFrame API
    if (!window.YT) {
      const tag = document.createElement('script');
      tag.src = 'https://www.youtube.com/iframe_api';
      const firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

      window.onYouTubeIframeAPIReady = initializePlayer;
    } else {
      initializePlayer();
    }

    return () => {
      if (progressUpdateInterval.current) {
        clearInterval(progressUpdateInterval.current);
      }
    };
  }, [video?.youtube_id]);

  const initializePlayer = () => {
    if (!playerRef.current) return;

    const player = new window.YT.Player(playerRef.current, {
      height: '100%',
      width: '100%',
      videoId: video.youtube_id,
      playerVars: {
        autoplay: autoplay ? 1 : 0,
        controls: showControls ? 1 : 0,
        modestbranding: 1,
        rel: 0,
        showinfo: 0,
        fs: 1,
        cc_load_policy: 1,
        iv_load_policy: 3,
        autohide: 0
      },
      events: {
        onReady: onPlayerReady,
        onStateChange: onPlayerStateChange,
        onError: onPlayerError
      }
    });

    window.ytPlayer = player;
  };

  const onPlayerReady = (event) => {
    const player = event.target;
    setDuration(player.getDuration());
    
    // Set initial position if user has progress
    if (video.progress?.current_position_seconds) {
      player.seekTo(video.progress.current_position_seconds, true);
      setCurrentTime(video.progress.current_position_seconds);
    }

    // Start progress tracking
    startProgressTracking();
  };

  const onPlayerStateChange = (event) => {
    const player = event.target;
    const state = event.data;

    switch (state) {
      case window.YT.PlayerState.PLAYING:
        setIsPlaying(true);
        startProgressTracking();
        updateEngagementMetrics('play');
        break;
      case window.YT.PlayerState.PAUSED:
        setIsPlaying(false);
        stopProgressTracking();
        updateEngagementMetrics('pause');
        break;
      case window.YT.PlayerState.ENDED:
        setIsPlaying(false);
        stopProgressTracking();
        updateEngagementMetrics('complete');
        break;
      case window.YT.PlayerState.BUFFERING:
        // Handle buffering if needed
        break;
    }
  };

  const onPlayerError = (event) => {
    console.error('YouTube Player Error:', event.data);
    // Handle player errors (video unavailable, etc.)
  };

  const startProgressTracking = () => {
    if (progressUpdateInterval.current) return;

    progressUpdateInterval.current = setInterval(() => {
      if (window.ytPlayer && typeof window.ytPlayer.getCurrentTime === 'function') {
        const currentTime = window.ytPlayer.getCurrentTime();
        const duration = window.ytPlayer.getDuration();
        
        setCurrentTime(currentTime);
        setDuration(duration);

        // Update progress every 5 seconds
        const now = Date.now();
        if (now - lastProgressUpdate.current >= 5000) {
          const watchTimeIncrement = Math.min(5, currentTime - (video.progress?.current_position_seconds || 0));
          
          if (onProgressUpdate) {
            onProgressUpdate({
              current_position_seconds: Math.floor(currentTime),
              watch_time_increment: Math.max(0, watchTimeIncrement),
              playback_quality: quality
            });
          }
          
          lastProgressUpdate.current = now;
        }
      }
    }, 1000);
  };

  const stopProgressTracking = () => {
    if (progressUpdateInterval.current) {
      clearInterval(progressUpdateInterval.current);
      progressUpdateInterval.current = null;
    }
  };

  const updateEngagementMetrics = (action) => {
    if (!onProgressUpdate) return;

    const metrics = {};
    switch (action) {
      case 'play':
        metrics.play_count_increment = 1;
        break;
      case 'pause':
        metrics.pause_count_increment = 1;
        break;
      case 'seek':
        metrics.seek_count_increment = 1;
        break;
    }

    if (Object.keys(metrics).length > 0) {
      onProgressUpdate(metrics);
    }
  };

  const handlePlayPause = () => {
    if (!window.ytPlayer) return;

    if (isPlaying) {
      window.ytPlayer.pauseVideo();
    } else {
      window.ytPlayer.playVideo();
    }
  };

  const handleSeek = (newTime) => {
    if (!window.ytPlayer) return;
    
    window.ytPlayer.seekTo(newTime, true);
    setCurrentTime(newTime);
    updateEngagementMetrics('seek');
  };

  const handleVolumeChange = (newVolume) => {
    if (!window.ytPlayer) return;
    
    setVolume(newVolume);
    window.ytPlayer.setVolume(newVolume * 100);
    setIsMuted(newVolume === 0);
  };

  const toggleMute = () => {
    if (!window.ytPlayer) return;
    
    if (isMuted) {
      window.ytPlayer.unMute();
      setIsMuted(false);
    } else {
      window.ytPlayer.mute();
      setIsMuted(true);
    }
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      playerRef.current?.parentElement?.requestFullscreen?.();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen?.();
      setIsFullscreen(false);
    }
  };

  const handleBookmarkToggle = () => {
    if (onBookmarkToggle) {
      onBookmarkToggle();
    }
  };

  const handleCreateBookmark = () => {
    setShowBookmarkForm(true);
  };

  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '0:00';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const progressPercentage = duration > 0 ? (currentTime / duration) * 100 : 0;

  if (!video) {
    return (
      <div className="w-full h-64 bg-gray-100 rounded-lg flex items-center justify-center">
        <p className="text-gray-500">No video selected</p>
      </div>
    );
  }

  return (
    <div className="relative w-full bg-black rounded-lg overflow-hidden">
      {/* Video Player Container */}
      <div className="relative w-full" style={{ paddingBottom: '56.25%' }}>
        <div
          ref={playerRef}
          className="absolute top-0 left-0 w-full h-full"
        />
        
        {/* Custom Controls Overlay */}
        {showControls && (
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
            {/* Progress Bar */}
            <div className="mb-4">
              <div className="relative w-full h-1 bg-white/30 rounded-full cursor-pointer">
                <div
                  className="absolute top-0 left-0 h-full bg-blue-500 rounded-full"
                  style={{ width: `${progressPercentage}%` }}
                />
                <input
                  type="range"
                  min="0"
                  max={duration}
                  value={currentTime}
                  onChange={(e) => handleSeek(parseFloat(e.target.value))}
                  className="absolute top-0 left-0 w-full h-full opacity-0 cursor-pointer"
                />
              </div>
            </div>

            {/* Control Buttons */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                {/* Play/Pause */}
                <button
                  onClick={handlePlayPause}
                  className="text-white hover:text-blue-400 transition-colors"
                >
                  {isPlaying ? <Pause size={24} /> : <Play size={24} />}
                </button>

                {/* Volume */}
                <div className="flex items-center space-x-2">
                  <button
                    onClick={toggleMute}
                    className="text-white hover:text-blue-400 transition-colors"
                  >
                    {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
                  </button>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={volume}
                    onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                    className="w-16 h-1 bg-white/30 rounded-full"
                  />
                </div>

                {/* Time Display */}
                <span className="text-white text-sm">
                  {formatTime(currentTime)} / {formatTime(duration)}
                </span>
              </div>

              <div className="flex items-center space-x-4">
                {/* Bookmark */}
                <button
                  onClick={handleBookmarkToggle}
                  className="text-white hover:text-yellow-400 transition-colors"
                  title="Bookmark this video"
                >
                  {video.progress?.is_bookmarked ? (
                    <BookmarkCheck size={20} />
                  ) : (
                    <Bookmark size={20} />
                  )}
                </button>

                {/* Create Timestamp Bookmark */}
                <button
                  onClick={handleCreateBookmark}
                  className="text-white hover:text-blue-400 transition-colors text-sm"
                  title="Create bookmark at current time"
                >
                  + Note
                </button>

                {/* Quality Settings */}
                <button
                  className="text-white hover:text-blue-400 transition-colors"
                  title="Quality settings"
                >
                  <Settings size={20} />
                </button>

                {/* Fullscreen */}
                <button
                  onClick={toggleFullscreen}
                  className="text-white hover:text-blue-400 transition-colors"
                >
                  <Maximize size={20} />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Video Info */}
      <div className="p-4 bg-white">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {video.title}
        </h3>
        
        {video.description && (
          <p className="text-gray-600 text-sm mb-3">
            {video.description}
          </p>
        )}

        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center space-x-4">
            <span>Duration: {video.duration_formatted}</span>
            <span>Type: {video.video_type}</span>
            <span>Level: {video.difficulty_level}</span>
          </div>
          
          {video.progress && (
            <div className="flex items-center space-x-2">
              <div className="w-16 h-2 bg-gray-200 rounded-full">
                <div
                  className="h-full bg-blue-500 rounded-full"
                  style={{ width: `${video.progress.completion_percentage}%` }}
                />
              </div>
              <span>{Math.round(video.progress.completion_percentage)}%</span>
            </div>
          )}
        </div>

        {/* Tags */}
        {video.tags && video.tags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {video.tags.map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Bookmark Form Modal */}
      {showBookmarkForm && (
        <BookmarkForm
          videoId={video.id}
          currentTime={currentTime}
          onClose={() => setShowBookmarkForm(false)}
          onSave={(bookmark) => {
            // Handle bookmark save
            setShowBookmarkForm(false);
          }}
        />
      )}
    </div>
  );
};

// Bookmark Form Component
const BookmarkForm = ({ videoId, currentTime, onClose, onSave }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [type, setType] = useState('note');

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const bookmark = {
      video_id: videoId,
      timestamp_seconds: Math.floor(currentTime),
      title,
      description,
      bookmark_type: type
    };

    onSave(bookmark);
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">
          Create Bookmark at {formatTime(currentTime)}
        </h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Bookmark title"
              required
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
              placeholder="Optional description"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type
            </label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="note">Note</option>
              <option value="question">Question</option>
              <option value="important">Important</option>
              <option value="review">Review Later</option>
            </select>
          </div>

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Save Bookmark
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default VideoPlayer;

