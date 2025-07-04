#!/usr/bin/env python3
"""
Simple script to create sample knowledge base data
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def create_sample_data():
    """Create sample knowledge base data using the main app"""
    try:
        # Import after path setup
        from src.main import create_app
        from src.models.knowledge_base import db, ResourceCategory, KnowledgeResource
        
        app = create_app()
        
        with app.app_context():
            # Create categories
            categories_data = [
                ('AI Governance', 'Resources for AI governance frameworks and policies'),
                ('Risk Management', 'AI risk assessment and management resources'),
                ('Compliance', 'Compliance guides and regulatory resources'),
                ('Implementation', 'Practical implementation guides and templates'),
                ('Training Materials', 'Educational content and training resources')
            ]

            categories = []
            for name, desc in categories_data:
                category = ResourceCategory(name=name, description=desc, slug=name.lower().replace(' ', '-'))
                db.session.add(category)
                categories.append(category)

            db.session.flush()  # Get IDs

            # Create sample resources
            resources_data = [
                {
                    'title': 'ISO/IEC 42001:2023 Standard Document',
                    'description': 'Complete ISO/IEC 42001:2023 standard for AI management systems',
                    'resource_type': 'standard',
                    'file_format': 'pdf',
                    'file_size': 2048000,
                    'author': 'ISO/IEC',
                    'category_id': categories[0].id,
                    'is_featured': True
                },
                {
                    'title': 'AI Risk Assessment Template',
                    'description': 'Comprehensive template for conducting AI risk assessments',
                    'resource_type': 'template',
                    'file_format': 'xlsx',
                    'file_size': 512000,
                    'author': 'Qryti Experts',
                    'category_id': categories[1].id,
                    'is_featured': True
                },
                {
                    'title': 'AI Governance Policy Template',
                    'description': 'Ready-to-use policy template for AI governance implementation',
                    'resource_type': 'template',
                    'file_format': 'docx',
                    'file_size': 256000,
                    'author': 'Qryti Legal Team',
                    'category_id': categories[0].id
                },
                {
                    'title': 'Compliance Checklist for AI Systems',
                    'description': 'Step-by-step checklist for ensuring AI system compliance',
                    'resource_type': 'checklist',
                    'file_format': 'pdf',
                    'file_size': 128000,
                    'author': 'Compliance Team',
                    'category_id': categories[2].id
                },
                {
                    'title': 'AI Ethics Implementation Guide',
                    'description': 'Practical guide for implementing AI ethics in organizations',
                    'resource_type': 'guide',
                    'file_format': 'pdf',
                    'file_size': 1024000,
                    'author': 'Dr. Sarah Chen',
                    'category_id': categories[3].id,
                    'is_featured': True
                }
            ]

            for res_data in resources_data:
                resource = KnowledgeResource(
                    title=res_data['title'],
                    description=res_data['description'],
                    resource_type=res_data['resource_type'],
                    file_format=res_data['file_format'],
                    file_size_bytes=res_data['file_size'],
                    author=res_data['author'],
                    category_id=res_data['category_id'],
                    is_featured=res_data.get('is_featured', False),
                    download_count=0,
                    view_count=0,
                    rating_sum=45,
                    rating_count=10,
                    created_at=datetime.utcnow() - timedelta(days=30),
                    updated_at=datetime.utcnow()
                )
                db.session.add(resource)

            # Commit all changes
            db.session.commit()
            print("✅ Sample knowledge base data created successfully!")
            print(f"Created {len(categories)} categories")
            print(f"Created {len(resources_data)} resources")

    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_sample_data()

