"""
Video API Routes for Qryti Learn
Handles video content, YouTube integration, and progress tracking
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import re

from ..models.user import db, User
from ..models.video import Video, VideoProgress, VideoBookmark
from ..models.course import Course, Module

videos_bp = Blueprint('videos', __name__)

def extract_youtube_id(url):
    """Extract YouTube video ID from various URL formats"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@videos_bp.route('/videos', methods=['GET'])
@jwt_required()
def get_videos():
    """Get all videos for a user with progress"""
    try:
        user_id = get_jwt_identity()
        course_id = request.args.get('course_id', type=int)
        module_id = request.args.get('module_id', type=int)
        video_type = request.args.get('type')
        
        # Build query
        query = Video.query.filter_by(is_active=True)
        
        if course_id:
            query = query.filter_by(course_id=course_id)
        
        if module_id:
            query = query.filter_by(module_id=module_id)
        
        if video_type:
            query = query.filter_by(video_type=video_type)
        
        videos = query.order_by(Video.order_index, Video.created_at).all()
        
        # Get user progress for each video
        video_data = []
        for video in videos:
            video_dict = video.to_dict()
            
            # Get user progress
            progress = VideoProgress.query.filter_by(
                user_id=user_id,
                video_id=video.id
            ).first()
            
            if progress:
                video_dict['progress'] = progress.to_dict()
            else:
                video_dict['progress'] = None
            
            video_data.append(video_dict)
        
        return jsonify({
            'videos': video_data,
            'total': len(video_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@videos_bp.route('/videos/<int:video_id>', methods=['GET'])
@jwt_required()
def get_video(video_id):
    """Get specific video with user progress"""
    try:
        user_id = get_jwt_identity()
        
        video = Video.query.get_or_404(video_id)
        
        if not video.is_active:
            return jsonify({'error': 'Video not available'}), 404
        
        video_dict = video.to_dict()
        
        # Get user progress
        progress = VideoProgress.query.filter_by(
            user_id=user_id,
            video_id=video_id
        ).first()
        
        if progress:
            video_dict['progress'] = progress.to_dict()
        else:
            video_dict['progress'] = None
        
        # Get user bookmarks for this video
        bookmarks = VideoBookmark.query.filter_by(
            user_id=user_id,
            video_id=video_id
        ).order_by(VideoBookmark.timestamp_seconds).all()
        
        video_dict['bookmarks'] = [bookmark.to_dict() for bookmark in bookmarks]
        
        return jsonify(video_dict)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@videos_bp.route('/videos/<int:video_id>/progress', methods=['POST'])
@jwt_required()
def update_video_progress():
    """Update video progress for a user"""
    try:
        user_id = get_jwt_identity()
        video_id = request.view_args['video_id']
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        video = Video.query.get_or_404(video_id)
        
        # Get or create progress record
        progress = VideoProgress.query.filter_by(
            user_id=user_id,
            video_id=video_id
        ).first()
        
        if not progress:
            progress = VideoProgress(
                user_id=user_id,
                video_id=video_id
            )
            db.session.add(progress)
        
        # Update progress data
        current_position = data.get('current_position_seconds', progress.current_position_seconds)
        watch_time_increment = data.get('watch_time_increment', 0)
        
        progress.update_progress(current_position, watch_time_increment)
        
        # Update engagement metrics
        if 'play_count_increment' in data:
            progress.play_count += data['play_count_increment']
        
        if 'pause_count_increment' in data:
            progress.pause_count += data['pause_count_increment']
        
        if 'seek_count_increment' in data:
            progress.seek_count += data['seek_count_increment']
        
        if 'playback_quality' in data:
            progress.playback_quality = data['playback_quality']
        
        if 'average_engagement' in data:
            progress.average_engagement = data['average_engagement']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Progress updated successfully',
            'progress': progress.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@videos_bp.route('/videos/<int:video_id>/bookmark', methods=['POST'])
@jwt_required()
def toggle_video_bookmark():
    """Toggle video bookmark status"""
    try:
        user_id = get_jwt_identity()
        video_id = request.view_args['video_id']
        
        video = Video.query.get_or_404(video_id)
        
        # Get or create progress record
        progress = VideoProgress.query.filter_by(
            user_id=user_id,
            video_id=video_id
        ).first()
        
        if not progress:
            progress = VideoProgress(
                user_id=user_id,
                video_id=video_id
            )
            db.session.add(progress)
        
        # Toggle bookmark status
        progress.is_bookmarked = not progress.is_bookmarked
        
        db.session.commit()
        
        return jsonify({
            'message': 'Bookmark toggled successfully',
            'is_bookmarked': progress.is_bookmarked
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@videos_bp.route('/videos/<int:video_id>/bookmarks', methods=['POST'])
@jwt_required()
def create_video_bookmark():
    """Create a timestamp bookmark for a video"""
    try:
        user_id = get_jwt_identity()
        video_id = request.view_args['video_id']
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['timestamp_seconds', 'title']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        video = Video.query.get_or_404(video_id)
        
        # Create bookmark
        bookmark = VideoBookmark(
            user_id=user_id,
            video_id=video_id,
            timestamp_seconds=data['timestamp_seconds'],
            title=data['title'],
            description=data.get('description', ''),
            bookmark_type=data.get('bookmark_type', 'note')
        )
        
        if 'tags' in data:
            bookmark.tags = data['tags']
        
        db.session.add(bookmark)
        db.session.commit()
        
        return jsonify({
            'message': 'Bookmark created successfully',
            'bookmark': bookmark.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@videos_bp.route('/videos/<int:video_id>/bookmarks/<int:bookmark_id>', methods=['DELETE'])
@jwt_required()
def delete_video_bookmark():
    """Delete a video bookmark"""
    try:
        user_id = get_jwt_identity()
        video_id = request.view_args['video_id']
        bookmark_id = request.view_args['bookmark_id']
        
        bookmark = VideoBookmark.query.filter_by(
            id=bookmark_id,
            user_id=user_id,
            video_id=video_id
        ).first_or_404()
        
        db.session.delete(bookmark)
        db.session.commit()
        
        return jsonify({'message': 'Bookmark deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@videos_bp.route('/videos/progress/summary', methods=['GET'])
@jwt_required()
def get_video_progress_summary():
    """Get video progress summary for a user"""
    try:
        user_id = get_jwt_identity()
        course_id = request.args.get('course_id', type=int)
        
        # Build query for user's video progress
        query = VideoProgress.query.filter_by(user_id=user_id)
        
        if course_id:
            query = query.join(Video).filter(Video.course_id == course_id)
        
        progress_records = query.all()
        
        # Calculate summary statistics
        total_videos = len(progress_records)
        completed_videos = len([p for p in progress_records if p.is_completed])
        total_watch_time = sum(p.watch_time_seconds for p in progress_records)
        bookmarked_videos = len([p for p in progress_records if p.is_bookmarked])
        
        # Calculate average completion percentage
        avg_completion = 0
        if total_videos > 0:
            avg_completion = sum(p.completion_percentage for p in progress_records) / total_videos
        
        # Format total watch time
        hours = total_watch_time // 3600
        minutes = (total_watch_time % 3600) // 60
        
        return jsonify({
            'total_videos': total_videos,
            'completed_videos': completed_videos,
            'completion_rate': (completed_videos / total_videos * 100) if total_videos > 0 else 0,
            'average_completion_percentage': round(avg_completion, 1),
            'total_watch_time_seconds': total_watch_time,
            'total_watch_time_formatted': f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m",
            'bookmarked_videos': bookmarked_videos,
            'recent_activity': [
                {
                    'video_id': p.video_id,
                    'video_title': p.video.title if p.video else 'Unknown',
                    'last_watched_at': p.last_watched_at.isoformat() if p.last_watched_at else None,
                    'completion_percentage': p.completion_percentage
                }
                for p in sorted(progress_records, key=lambda x: x.last_watched_at or datetime.min, reverse=True)[:5]
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@videos_bp.route('/videos/bookmarked', methods=['GET'])
@jwt_required()
def get_bookmarked_videos():
    """Get all bookmarked videos for a user"""
    try:
        user_id = get_jwt_identity()
        
        # Get videos that are bookmarked (either as favorite or have timestamp bookmarks)
        bookmarked_progress = VideoProgress.query.filter_by(
            user_id=user_id,
            is_bookmarked=True
        ).all()
        
        timestamp_bookmarks = VideoBookmark.query.filter_by(
            user_id=user_id
        ).all()
        
        # Combine and organize results
        bookmarked_videos = []
        
        # Add favorited videos
        for progress in bookmarked_progress:
            if progress.video and progress.video.is_active:
                video_dict = progress.video.to_dict()
                video_dict['progress'] = progress.to_dict()
                video_dict['bookmark_type'] = 'favorite'
                bookmarked_videos.append(video_dict)
        
        # Add videos with timestamp bookmarks
        video_ids_with_bookmarks = set()
        for bookmark in timestamp_bookmarks:
            if bookmark.video and bookmark.video.is_active:
                video_id = bookmark.video_id
                if video_id not in video_ids_with_bookmarks:
                    video_ids_with_bookmarks.add(video_id)
                    
                    video_dict = bookmark.video.to_dict()
                    
                    # Get progress if exists
                    progress = VideoProgress.query.filter_by(
                        user_id=user_id,
                        video_id=video_id
                    ).first()
                    
                    if progress:
                        video_dict['progress'] = progress.to_dict()
                    
                    video_dict['bookmark_type'] = 'timestamp'
                    video_dict['bookmark_count'] = len([b for b in timestamp_bookmarks if b.video_id == video_id])
                    bookmarked_videos.append(video_dict)
        
        return jsonify({
            'bookmarked_videos': bookmarked_videos,
            'total': len(bookmarked_videos)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin routes for video management
@videos_bp.route('/admin/videos', methods=['POST'])
@jwt_required()
def create_video():
    """Create a new video (admin only)"""
    try:
        # Note: In production, add admin role check here
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['title', 'youtube_url', 'module_id', 'course_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Extract YouTube ID from URL
        youtube_id = extract_youtube_id(data['youtube_url'])
        if not youtube_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        
        # Check if video already exists
        existing_video = Video.query.filter_by(youtube_id=youtube_id).first()
        if existing_video:
            return jsonify({'error': 'Video with this YouTube ID already exists'}), 400
        
        # Verify module and course exist
        module = Module.query.get(data['module_id'])
        course = Course.query.get(data['course_id'])
        
        if not module:
            return jsonify({'error': 'Module not found'}), 404
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Create video
        video = Video(
            title=data['title'],
            description=data.get('description', ''),
            youtube_id=youtube_id,
            youtube_url=data['youtube_url'],
            thumbnail_url=data.get('thumbnail_url', f"https://img.youtube.com/vi/{youtube_id}/maxresdefault.jpg"),
            duration_seconds=data.get('duration_seconds', 0),
            video_type=data.get('video_type', 'lesson'),
            difficulty_level=data.get('difficulty_level', 'beginner'),
            module_id=data['module_id'],
            course_id=data['course_id'],
            order_index=data.get('order_index', 0),
            is_preview=data.get('is_preview', False),
            transcript_url=data.get('transcript_url'),
            captions_url=data.get('captions_url')
        )
        
        if 'tags' in data:
            video.tags = data['tags']
        
        db.session.add(video)
        db.session.commit()
        
        return jsonify({
            'message': 'Video created successfully',
            'video': video.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

