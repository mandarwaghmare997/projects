"""
Video Models for Qryti Learn
Handles video content, YouTube integration, and progress tracking
"""

from datetime import datetime
from .user import db
import json

class Video(db.Model):
    """Video content model for course modules"""
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # YouTube integration
    youtube_id = db.Column(db.String(50), unique=True, nullable=False)
    youtube_url = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(500))
    
    # Video metadata
    duration_seconds = db.Column(db.Integer, default=0)  # Video duration in seconds
    video_type = db.Column(db.String(50), default='lesson')  # lesson, tutorial, demo, etc.
    difficulty_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    
    # Course relationship
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    # Ordering and organization
    order_index = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    is_preview = db.Column(db.Boolean, default=False)  # Can be viewed without enrollment
    
    # Metadata and tags
    tags_json = db.Column(db.Text)  # JSON array of tags
    transcript_url = db.Column(db.String(500))  # URL to transcript file
    captions_url = db.Column(db.String(500))  # URL to captions file
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    module = db.relationship('Module', backref='videos')
    course = db.relationship('Course', backref='videos')
    progress_records = db.relationship('VideoProgress', backref='video', cascade='all, delete-orphan')
    
    @property
    def tags(self):
        """Get tags as a list"""
        if self.tags_json:
            try:
                return json.loads(self.tags_json)
            except:
                return []
        return []
    
    @tags.setter
    def tags(self, value):
        """Set tags from a list"""
        if isinstance(value, list):
            self.tags_json = json.dumps(value)
        else:
            self.tags_json = json.dumps([])
    
    @property
    def duration_formatted(self):
        """Get formatted duration (MM:SS or HH:MM:SS)"""
        if not self.duration_seconds:
            return "0:00"
        
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    @property
    def embed_url(self):
        """Get YouTube embed URL"""
        return f"https://www.youtube.com/embed/{self.youtube_id}"
    
    def to_dict(self):
        """Convert video to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'youtube_id': self.youtube_id,
            'youtube_url': self.youtube_url,
            'embed_url': self.embed_url,
            'thumbnail_url': self.thumbnail_url,
            'duration_seconds': self.duration_seconds,
            'duration_formatted': self.duration_formatted,
            'video_type': self.video_type,
            'difficulty_level': self.difficulty_level,
            'module_id': self.module_id,
            'course_id': self.course_id,
            'order_index': self.order_index,
            'is_active': self.is_active,
            'is_preview': self.is_preview,
            'tags': self.tags,
            'transcript_url': self.transcript_url,
            'captions_url': self.captions_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class VideoProgress(db.Model):
    """Video progress tracking for users"""
    __tablename__ = 'video_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    
    # Progress tracking
    watch_time_seconds = db.Column(db.Integer, default=0)  # Total time watched
    current_position_seconds = db.Column(db.Integer, default=0)  # Current playback position
    completion_percentage = db.Column(db.Float, default=0.0)  # Percentage completed (0-100)
    
    # Status tracking
    is_completed = db.Column(db.Boolean, default=False)
    is_bookmarked = db.Column(db.Boolean, default=False)
    last_watched_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Engagement metrics
    play_count = db.Column(db.Integer, default=0)  # Number of times played
    pause_count = db.Column(db.Integer, default=0)  # Number of times paused
    seek_count = db.Column(db.Integer, default=0)  # Number of times seeked
    
    # Quality and engagement
    playback_quality = db.Column(db.String(20))  # 720p, 1080p, etc.
    average_engagement = db.Column(db.Float, default=0.0)  # Engagement score (0-1)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='video_progress')
    
    # Unique constraint to prevent duplicate progress records
    __table_args__ = (db.UniqueConstraint('user_id', 'video_id', name='unique_user_video_progress'),)
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage based on watch time"""
        if not self.video or not self.video.duration_seconds:
            return 0.0
        
        return min(100.0, (self.watch_time_seconds / self.video.duration_seconds) * 100)
    
    @property
    def remaining_time_seconds(self):
        """Get remaining time in seconds"""
        if not self.video or not self.video.duration_seconds:
            return 0
        
        return max(0, self.video.duration_seconds - self.current_position_seconds)
    
    @property
    def remaining_time_formatted(self):
        """Get formatted remaining time"""
        remaining = self.remaining_time_seconds
        if remaining <= 0:
            return "0:00"
        
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        seconds = remaining % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def update_progress(self, current_position, watch_time_increment=0):
        """Update video progress"""
        self.current_position_seconds = current_position
        self.watch_time_seconds += watch_time_increment
        self.last_watched_at = datetime.utcnow()
        
        # Calculate completion percentage
        if self.video and self.video.duration_seconds > 0:
            self.completion_percentage = min(100.0, (self.current_position_seconds / self.video.duration_seconds) * 100)
            
            # Mark as completed if watched 90% or more
            if self.completion_percentage >= 90.0 and not self.is_completed:
                self.is_completed = True
                self.completed_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert progress to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'video_id': self.video_id,
            'watch_time_seconds': self.watch_time_seconds,
            'current_position_seconds': self.current_position_seconds,
            'completion_percentage': self.completion_percentage,
            'progress_percentage': self.progress_percentage,
            'is_completed': self.is_completed,
            'is_bookmarked': self.is_bookmarked,
            'last_watched_at': self.last_watched_at.isoformat() if self.last_watched_at else None,
            'play_count': self.play_count,
            'pause_count': self.pause_count,
            'seek_count': self.seek_count,
            'playback_quality': self.playback_quality,
            'average_engagement': self.average_engagement,
            'remaining_time_seconds': self.remaining_time_seconds,
            'remaining_time_formatted': self.remaining_time_formatted,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class VideoBookmark(db.Model):
    """Video bookmarks for specific timestamps"""
    __tablename__ = 'video_bookmarks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    
    # Bookmark details
    timestamp_seconds = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Organization
    bookmark_type = db.Column(db.String(50), default='note')  # note, question, important, etc.
    tags_json = db.Column(db.Text)  # JSON array of tags
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='video_bookmarks')
    video = db.relationship('Video', backref='bookmarks')
    
    @property
    def tags(self):
        """Get tags as a list"""
        if self.tags_json:
            try:
                return json.loads(self.tags_json)
            except:
                return []
        return []
    
    @tags.setter
    def tags(self, value):
        """Set tags from a list"""
        if isinstance(value, list):
            self.tags_json = json.dumps(value)
        else:
            self.tags_json = json.dumps([])
    
    @property
    def timestamp_formatted(self):
        """Get formatted timestamp (MM:SS or HH:MM:SS)"""
        hours = self.timestamp_seconds // 3600
        minutes = (self.timestamp_seconds % 3600) // 60
        seconds = self.timestamp_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def to_dict(self):
        """Convert bookmark to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'video_id': self.video_id,
            'timestamp_seconds': self.timestamp_seconds,
            'timestamp_formatted': self.timestamp_formatted,
            'title': self.title,
            'description': self.description,
            'bookmark_type': self.bookmark_type,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

