"""
Knowledge Base API Routes for Qryti Learn
Handles downloadable resources, documents, and knowledge management
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_required
from datetime import datetime
from sqlalchemy import or_, and_, desc, asc
import os
import hashlib
import mimetypes

from ..models.user import db, User
from ..models.knowledge_base import (
    ResourceCategory, KnowledgeResource, ResourceDownload, 
    ResourceBookmark, ResourceRating, ResourceCollection, ResourceCollectionItem
)

knowledge_base_bp = Blueprint('knowledge_base', __name__)

# Category Management Routes

@knowledge_base_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all resource categories"""
    try:
        categories = ResourceCategory.query.filter_by(is_active=True).order_by(
            ResourceCategory.order_index, ResourceCategory.name
        ).all()
        
        # Organize categories hierarchically
        root_categories = []
        category_dict = {}
        
        for category in categories:
            category_dict[category.id] = category.to_dict()
            if category.parent_id is None:
                root_categories.append(category_dict[category.id])
        
        # Add subcategories to their parents
        for category in categories:
            if category.parent_id is not None:
                parent = category_dict.get(category.parent_id)
                if parent:
                    if 'subcategories' not in parent:
                        parent['subcategories'] = []
                    parent['subcategories'].append(category_dict[category.id])
        
        return jsonify({
            'categories': root_categories,
            'total': len(categories)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@knowledge_base_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get specific category with resources"""
    try:
        category = ResourceCategory.query.get_or_404(category_id)
        
        if not category.is_active:
            return jsonify({'error': 'Category not found'}), 404
        
        category_dict = category.to_dict()
        
        # Get resources in this category
        resources = KnowledgeResource.query.filter_by(
            category_id=category_id,
            is_active=True
        ).order_by(KnowledgeResource.order_index, KnowledgeResource.title).all()
        
        category_dict['resources'] = [resource.to_dict() for resource in resources]
        
        return jsonify(category_dict)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Resource Management Routes

@knowledge_base_bp.route('/resources', methods=['GET'])
def get_resources():
    """Get resources with filtering and pagination"""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        category_id = request.args.get('category_id', type=int)
        resource_type = request.args.get('type')
        search = request.args.get('search', '').strip()
        tags = request.args.get('tags', '').strip()
        sort_by = request.args.get('sort', 'title')  # title, created_at, download_count, rating
        order = request.args.get('order', 'asc')  # asc, desc
        featured_only = request.args.get('featured', 'false').lower() == 'true'
        
        # Build query
        query = KnowledgeResource.query.filter_by(is_active=True)
        
        # Apply filters
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if resource_type:
            query = query.filter_by(resource_type=resource_type)
        
        if featured_only:
            query = query.filter_by(is_featured=True)
        
        # Search functionality
        if search:
            search_filter = or_(
                KnowledgeResource.title.ilike(f'%{search}%'),
                KnowledgeResource.description.ilike(f'%{search}%'),
                KnowledgeResource.content.ilike(f'%{search}%'),
                KnowledgeResource.keywords.ilike(f'%{search}%'),
                KnowledgeResource.author.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # Tag filtering
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag in tag_list:
                query = query.filter(KnowledgeResource.tags_json.ilike(f'%{tag}%'))
        
        # Sorting
        sort_column = KnowledgeResource.title  # default
        if sort_by == 'created_at':
            sort_column = KnowledgeResource.created_at
        elif sort_by == 'download_count':
            sort_column = KnowledgeResource.download_count
        elif sort_by == 'rating':
            sort_column = KnowledgeResource.rating_sum / KnowledgeResource.rating_count
        elif sort_by == 'updated_at':
            sort_column = KnowledgeResource.updated_at
        
        if order == 'desc':
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Pagination
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        resources = [resource.to_dict() for resource in pagination.items]
        
        return jsonify({
            'resources': resources,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@knowledge_base_bp.route('/resources/<int:resource_id>', methods=['GET'])
@jwt_required(optional=True)
def get_resource(resource_id):
    """Get specific resource details"""
    try:
        user_id = get_jwt_identity()
        resource = KnowledgeResource.query.get_or_404(resource_id)
        
        if not resource.is_active:
            return jsonify({'error': 'Resource not found'}), 404
        
        # Check access permissions
        if not resource.is_public and not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Increment view count
        resource.increment_view_count()
        
        resource_dict = resource.to_dict(include_content=True)
        
        # Add user-specific data if authenticated
        if user_id:
            # Check if user has bookmarked this resource
            bookmark = ResourceBookmark.query.filter_by(
                user_id=user_id,
                resource_id=resource_id
            ).first()
            resource_dict['is_bookmarked'] = bookmark is not None
            resource_dict['bookmark_notes'] = bookmark.notes if bookmark else None
            
            # Check if user has rated this resource
            rating = ResourceRating.query.filter_by(
                user_id=user_id,
                resource_id=resource_id
            ).first()
            resource_dict['user_rating'] = rating.rating if rating else None
            resource_dict['user_review'] = rating.review if rating else None
            
            # Check if user has downloaded this resource
            download = ResourceDownload.query.filter_by(
                user_id=user_id,
                resource_id=resource_id
            ).first()
            resource_dict['has_downloaded'] = download is not None
            resource_dict['last_downloaded'] = download.downloaded_at.isoformat() if download else None
        
        return jsonify(resource_dict)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@knowledge_base_bp.route('/resources/<int:resource_id>/download', methods=['POST'])
@jwt_required()
def download_resource(resource_id):
    """Download a resource file"""
    try:
        user_id = get_jwt_identity()
        resource = KnowledgeResource.query.get_or_404(resource_id)
        
        if not resource.is_active:
            return jsonify({'error': 'Resource not found'}), 404
        
        # Check access permissions
        if not resource.is_public:
            # Add role-based access control here if needed
            pass
        
        # Check if file exists
        if not resource.file_path or not os.path.exists(resource.file_path):
            return jsonify({'error': 'File not available for download'}), 404
        
        # Record download
        download = ResourceDownload(
            user_id=user_id,
            resource_id=resource_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            download_source='web'
        )
        db.session.add(download)
        
        # Increment download count
        resource.increment_download_count()
        
        db.session.commit()
        
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(resource.file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # Send file
        return send_file(
            resource.file_path,
            as_attachment=True,
            download_name=f"{resource.title}.{resource.file_extension}",
            mimetype=mime_type
        )
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@knowledge_base_bp.route('/resources/<int:resource_id>/bookmark', methods=['POST'])
@jwt_required()
def toggle_resource_bookmark(resource_id):
    """Toggle resource bookmark"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        resource = KnowledgeResource.query.get_or_404(resource_id)
        
        # Check if bookmark exists
        bookmark = ResourceBookmark.query.filter_by(
            user_id=user_id,
            resource_id=resource_id
        ).first()
        
        if bookmark:
            # Update existing bookmark
            bookmark.notes = data.get('notes', bookmark.notes)
            if 'tags' in data:
                bookmark.tags = data['tags']
            bookmark.updated_at = datetime.utcnow()
            action = 'updated'
        else:
            # Create new bookmark
            bookmark = ResourceBookmark(
                user_id=user_id,
                resource_id=resource_id,
                notes=data.get('notes', ''),
            )
            if 'tags' in data:
                bookmark.tags = data['tags']
            db.session.add(bookmark)
            action = 'created'
        
        db.session.commit()
        
        return jsonify({
            'message': f'Bookmark {action} successfully',
            'bookmark': bookmark.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@knowledge_base_bp.route('/resources/<int:resource_id>/bookmark', methods=['DELETE'])
@jwt_required()
def remove_resource_bookmark(resource_id):
    """Remove resource bookmark"""
    try:
        user_id = get_jwt_identity()
        
        bookmark = ResourceBookmark.query.filter_by(
            user_id=user_id,
            resource_id=resource_id
        ).first_or_404()
        
        db.session.delete(bookmark)
        db.session.commit()
        
        return jsonify({'message': 'Bookmark removed successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@knowledge_base_bp.route('/resources/<int:resource_id>/rating', methods=['POST'])
@jwt_required()
def rate_resource(resource_id):
    """Rate a resource"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'rating' not in data:
            return jsonify({'error': 'Rating is required'}), 400
        
        rating_value = data['rating']
        if not isinstance(rating_value, int) or rating_value < 1 or rating_value > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        resource = KnowledgeResource.query.get_or_404(resource_id)
        
        # Check if user has already rated this resource
        existing_rating = ResourceRating.query.filter_by(
            user_id=user_id,
            resource_id=resource_id
        ).first()
        
        if existing_rating:
            # Update existing rating
            old_rating = existing_rating.rating
            existing_rating.rating = rating_value
            existing_rating.review = data.get('review', existing_rating.review)
            existing_rating.updated_at = datetime.utcnow()
            
            # Update resource rating totals
            resource.rating_sum = resource.rating_sum - old_rating + rating_value
            
            action = 'updated'
            rating_obj = existing_rating
        else:
            # Create new rating
            rating_obj = ResourceRating(
                user_id=user_id,
                resource_id=resource_id,
                rating=rating_value,
                review=data.get('review', '')
            )
            db.session.add(rating_obj)
            
            # Update resource rating totals
            resource.rating_sum += rating_value
            resource.rating_count += 1
            
            action = 'created'
        
        db.session.commit()
        
        return jsonify({
            'message': f'Rating {action} successfully',
            'rating': rating_obj.to_dict(),
            'resource_average_rating': resource.average_rating
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User-specific routes

@knowledge_base_bp.route('/my/bookmarks', methods=['GET'])
@jwt_required()
def get_user_bookmarks():
    """Get user's bookmarked resources"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Get bookmarked resources
        query = db.session.query(ResourceBookmark, KnowledgeResource).join(
            KnowledgeResource, ResourceBookmark.resource_id == KnowledgeResource.id
        ).filter(
            ResourceBookmark.user_id == user_id,
            KnowledgeResource.is_active == True
        ).order_by(desc(ResourceBookmark.created_at))
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        bookmarks = []
        for bookmark, resource in pagination.items:
            resource_dict = resource.to_dict()
            resource_dict['bookmark'] = bookmark.to_dict()
            bookmarks.append(resource_dict)
        
        return jsonify({
            'bookmarks': bookmarks,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@knowledge_base_bp.route('/my/downloads', methods=['GET'])
@jwt_required()
def get_user_downloads():
    """Get user's download history"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Get download history
        query = db.session.query(ResourceDownload, KnowledgeResource).join(
            KnowledgeResource, ResourceDownload.resource_id == KnowledgeResource.id
        ).filter(
            ResourceDownload.user_id == user_id,
            KnowledgeResource.is_active == True
        ).order_by(desc(ResourceDownload.downloaded_at))
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        downloads = []
        for download, resource in pagination.items:
            resource_dict = resource.to_dict()
            resource_dict['download'] = download.to_dict()
            downloads.append(resource_dict)
        
        return jsonify({
            'downloads': downloads,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Statistics and Analytics

@knowledge_base_bp.route('/stats', methods=['GET'])
def get_knowledge_base_stats():
    """Get knowledge base statistics"""
    try:
        # Basic counts
        total_resources = KnowledgeResource.query.filter_by(is_active=True).count()
        total_categories = ResourceCategory.query.filter_by(is_active=True).count()
        total_downloads = ResourceDownload.query.count()
        
        # Popular resources (top 10 by downloads)
        popular_resources = KnowledgeResource.query.filter_by(is_active=True).order_by(
            desc(KnowledgeResource.download_count)
        ).limit(10).all()
        
        # Recent resources (last 10)
        recent_resources = KnowledgeResource.query.filter_by(is_active=True).order_by(
            desc(KnowledgeResource.created_at)
        ).limit(10).all()
        
        # Resource types distribution
        resource_types = db.session.query(
            KnowledgeResource.resource_type,
            db.func.count(KnowledgeResource.id).label('count')
        ).filter_by(is_active=True).group_by(KnowledgeResource.resource_type).all()
        
        return jsonify({
            'total_resources': total_resources,
            'total_categories': total_categories,
            'total_downloads': total_downloads,
            'popular_resources': [resource.to_dict() for resource in popular_resources],
            'recent_resources': [resource.to_dict() for resource in recent_resources],
            'resource_types': [{'type': rt[0], 'count': rt[1]} for rt in resource_types]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Search functionality

@knowledge_base_bp.route('/search', methods=['GET'])
def search_resources():
    """Advanced search for resources"""
    try:
        query_text = request.args.get('q', '').strip()
        if not query_text:
            return jsonify({'error': 'Search query is required'}), 400
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Build search query
        search_terms = query_text.split()
        search_filters = []
        
        for term in search_terms:
            term_filter = or_(
                KnowledgeResource.title.ilike(f'%{term}%'),
                KnowledgeResource.description.ilike(f'%{term}%'),
                KnowledgeResource.content.ilike(f'%{term}%'),
                KnowledgeResource.keywords.ilike(f'%{term}%'),
                KnowledgeResource.author.ilike(f'%{term}%'),
                KnowledgeResource.tags_json.ilike(f'%{term}%')
            )
            search_filters.append(term_filter)
        
        # Combine all search filters with AND
        combined_filter = and_(*search_filters) if len(search_filters) > 1 else search_filters[0]
        
        query = KnowledgeResource.query.filter(
            KnowledgeResource.is_active == True,
            combined_filter
        ).order_by(desc(KnowledgeResource.download_count))
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        results = [resource.to_dict() for resource in pagination.items]
        
        return jsonify({
            'query': query_text,
            'results': results,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

