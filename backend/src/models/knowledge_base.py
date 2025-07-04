"""
Knowledge Base Models for Qryti Learn
Handles downloadable resources, documents, and knowledge management
"""

from datetime import datetime
from .user import db
import json
import os

class ResourceCategory(db.Model):
    """Categories for organizing knowledge base resources"""
    __tablename__ = 'resource_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    
    # Organization
    parent_id = db.Column(db.Integer, db.ForeignKey('resource_categories.id'))
    order_index = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    # Styling
    icon = db.Column(db.String(50))  # Icon name for UI
    color = db.Column(db.String(20))  # Color code for UI
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = db.relationship('ResourceCategory', remote_side=[id], backref='subcategories')
    resources = db.relationship('KnowledgeResource', backref='category', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert category to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'slug': self.slug,
            'parent_id': self.parent_id,
            'order_index': self.order_index,
            'is_active': self.is_active,
            'icon': self.icon,
            'color': self.color,
            'resource_count': len(self.resources),
            'subcategory_count': len(self.subcategories),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class KnowledgeResource(db.Model):
    """Knowledge base resources and downloadable content"""
    __tablename__ = 'knowledge_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)  # Full text content for search
    
    # Resource type and format
    resource_type = db.Column(db.String(50), nullable=False)  # document, template, guide, checklist, etc.
    file_format = db.Column(db.String(20))  # pdf, docx, xlsx, pptx, etc.
    
    # File information
    file_path = db.Column(db.String(500))  # Local file path
    file_url = db.Column(db.String(500))  # Public URL (S3, CDN, etc.)
    file_size_bytes = db.Column(db.BigInteger, default=0)
    file_hash = db.Column(db.String(64))  # SHA-256 hash for integrity
    
    # Metadata
    author = db.Column(db.String(100))
    version = db.Column(db.String(20), default='1.0')
    language = db.Column(db.String(10), default='en')
    
    # Organization
    category_id = db.Column(db.Integer, db.ForeignKey('resource_categories.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))  # Optional course association
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'))  # Optional module association
    
    # Access control
    is_public = db.Column(db.Boolean, default=False)  # Public access without login
    is_premium = db.Column(db.Boolean, default=False)  # Requires premium access
    required_role = db.Column(db.String(50))  # Required user role
    
    # Status and visibility
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    order_index = db.Column(db.Integer, default=0)
    
    # SEO and discovery
    tags_json = db.Column(db.Text)  # JSON array of tags
    keywords = db.Column(db.Text)  # Comma-separated keywords for search
    slug = db.Column(db.String(200), unique=True)
    
    # Analytics
    download_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    rating_sum = db.Column(db.Integer, default=0)
    rating_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Relationships
    course = db.relationship('Course', backref='knowledge_resources')
    module = db.relationship('Module', backref='knowledge_resources')
    downloads = db.relationship('ResourceDownload', backref='resource', cascade='all, delete-orphan')
    bookmarks = db.relationship('ResourceBookmark', backref='resource', cascade='all, delete-orphan')
    ratings = db.relationship('ResourceRating', backref='resource', cascade='all, delete-orphan')
    
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
    def file_size_formatted(self):
        """Get formatted file size"""
        if not self.file_size_bytes:
            return "Unknown"
        
        size = self.file_size_bytes
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    @property
    def average_rating(self):
        """Calculate average rating"""
        if self.rating_count == 0:
            return 0.0
        return round(self.rating_sum / self.rating_count, 1)
    
    @property
    def file_extension(self):
        """Get file extension from file_path or file_format"""
        if self.file_path:
            return os.path.splitext(self.file_path)[1].lower().lstrip('.')
        return self.file_format or ''
    
    def increment_download_count(self):
        """Increment download counter"""
        self.download_count += 1
        db.session.commit()
    
    def increment_view_count(self):
        """Increment view counter"""
        self.view_count += 1
        db.session.commit()
    
    def to_dict(self, include_content=False):
        """Convert resource to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'resource_type': self.resource_type,
            'file_format': self.file_format,
            'file_url': self.file_url,
            'file_size_bytes': self.file_size_bytes,
            'file_size_formatted': self.file_size_formatted,
            'file_extension': self.file_extension,
            'author': self.author,
            'version': self.version,
            'language': self.language,
            'category_id': self.category_id,
            'course_id': self.course_id,
            'module_id': self.module_id,
            'is_public': self.is_public,
            'is_premium': self.is_premium,
            'required_role': self.required_role,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'order_index': self.order_index,
            'tags': self.tags,
            'keywords': self.keywords,
            'slug': self.slug,
            'download_count': self.download_count,
            'view_count': self.view_count,
            'average_rating': self.average_rating,
            'rating_count': self.rating_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
        
        if include_content:
            data['content'] = self.content
        
        return data

class ResourceDownload(db.Model):
    """Track resource downloads by users"""
    __tablename__ = 'resource_downloads'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('knowledge_resources.id'), nullable=False)
    
    # Download metadata
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    user_agent = db.Column(db.String(500))
    download_source = db.Column(db.String(100))  # web, mobile, api, etc.
    
    # Timestamps
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='resource_downloads')
    
    # Unique constraint to prevent duplicate tracking
    __table_args__ = (db.UniqueConstraint('user_id', 'resource_id', 'downloaded_at', name='unique_user_resource_download'),)
    
    def to_dict(self):
        """Convert download to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'download_source': self.download_source,
            'downloaded_at': self.downloaded_at.isoformat() if self.downloaded_at else None
        }

class ResourceBookmark(db.Model):
    """User bookmarks for knowledge resources"""
    __tablename__ = 'resource_bookmarks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('knowledge_resources.id'), nullable=False)
    
    # Bookmark metadata
    notes = db.Column(db.Text)  # User notes about the resource
    tags_json = db.Column(db.Text)  # User's personal tags
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='resource_bookmarks')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'resource_id', name='unique_user_resource_bookmark'),)
    
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
    
    def to_dict(self):
        """Convert bookmark to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'notes': self.notes,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ResourceRating(db.Model):
    """User ratings for knowledge resources"""
    __tablename__ = 'resource_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('knowledge_resources.id'), nullable=False)
    
    # Rating data
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text)  # Optional review text
    
    # Moderation
    is_approved = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='resource_ratings')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'resource_id', name='unique_user_resource_rating'),)
    
    def to_dict(self):
        """Convert rating to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'rating': self.rating,
            'review': self.review,
            'is_approved': self.is_approved,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_name': self.user.first_name + ' ' + self.user.last_name if self.user else 'Anonymous'
        }

class ResourceCollection(db.Model):
    """User-created collections of resources"""
    __tablename__ = 'resource_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Collection metadata
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    slug = db.Column(db.String(200))
    
    # Visibility
    is_public = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Organization
    tags_json = db.Column(db.Text)  # JSON array of tags
    order_index = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='resource_collections')
    items = db.relationship('ResourceCollectionItem', backref='collection', cascade='all, delete-orphan')
    
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
    def resource_count(self):
        """Get number of resources in collection"""
        return len(self.items)
    
    def to_dict(self):
        """Convert collection to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'slug': self.slug,
            'is_public': self.is_public,
            'is_featured': self.is_featured,
            'tags': self.tags,
            'order_index': self.order_index,
            'resource_count': self.resource_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_name': self.user.first_name + ' ' + self.user.last_name if self.user else 'Anonymous'
        }

class ResourceCollectionItem(db.Model):
    """Items in resource collections"""
    __tablename__ = 'resource_collection_items'
    
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('resource_collections.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('knowledge_resources.id'), nullable=False)
    
    # Organization
    order_index = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)  # User notes about why this resource is in the collection
    
    # Timestamps
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    resource = db.relationship('KnowledgeResource', backref='collection_items')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('collection_id', 'resource_id', name='unique_collection_resource'),)
    
    def to_dict(self):
        """Convert collection item to dictionary"""
        return {
            'id': self.id,
            'collection_id': self.collection_id,
            'resource_id': self.resource_id,
            'order_index': self.order_index,
            'notes': self.notes,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'resource': self.resource.to_dict() if self.resource else None
        }

