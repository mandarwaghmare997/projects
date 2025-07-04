#!/usr/bin/env python3
"""
Create sample knowledge base data for Qryti Learn
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.src.models.user import db
from backend.src.models.knowledge_base import (
    ResourceCategory, KnowledgeResource, ResourceDownload, 
    ResourceBookmark, ResourceRating
)
from backend.src.main import create_app

def create_sample_knowledge_base_data():
    """Create sample knowledge base data"""
    
    # Create categories
    categories_data = [
        {
            'name': 'ISO/IEC 42001 Standards',
            'description': 'Official standards and documentation for AI Management Systems',
            'slug': 'iso-42001-standards',
            'icon': 'FileText',
            'color': '#3B82F6',
            'order_index': 1
        },
        {
            'name': 'Implementation Guides',
            'description': 'Step-by-step guides for implementing AI management systems',
            'slug': 'implementation-guides',
            'icon': 'BookOpen',
            'color': '#10B981',
            'order_index': 2
        },
        {
            'name': 'Templates & Checklists',
            'description': 'Ready-to-use templates and checklists for compliance',
            'slug': 'templates-checklists',
            'icon': 'CheckSquare',
            'color': '#F59E0B',
            'order_index': 3
        },
        {
            'name': 'Case Studies',
            'description': 'Real-world implementation examples and success stories',
            'slug': 'case-studies',
            'icon': 'Users',
            'color': '#8B5CF6',
            'order_index': 4
        },
        {
            'name': 'Training Materials',
            'description': 'Educational resources and training materials',
            'slug': 'training-materials',
            'icon': 'GraduationCap',
            'color': '#EF4444',
            'order_index': 5
        },
        {
            'name': 'Tools & Software',
            'description': 'Software tools and utilities for AI management',
            'slug': 'tools-software',
            'icon': 'Settings',
            'color': '#06B6D4',
            'order_index': 6
        }
    ]
    
    categories = {}
    for cat_data in categories_data:
        category = ResourceCategory(**cat_data)
        db.session.add(category)
        db.session.flush()  # Get the ID
        categories[cat_data['slug']] = category
    
    # Create subcategories
    subcategories_data = [
        {
            'name': 'Risk Management',
            'description': 'AI risk assessment and management resources',
            'slug': 'risk-management',
            'parent_id': categories['implementation-guides'].id,
            'icon': 'Shield',
            'color': '#DC2626',
            'order_index': 1
        },
        {
            'name': 'Governance Framework',
            'description': 'AI governance and oversight frameworks',
            'slug': 'governance-framework',
            'parent_id': categories['implementation-guides'].id,
            'icon': 'Scale',
            'color': '#7C3AED',
            'order_index': 2
        },
        {
            'name': 'Audit Checklists',
            'description': 'Comprehensive audit and assessment checklists',
            'slug': 'audit-checklists',
            'parent_id': categories['templates-checklists'].id,
            'icon': 'ClipboardCheck',
            'color': '#059669',
            'order_index': 1
        }
    ]
    
    for subcat_data in subcategories_data:
        subcategory = ResourceCategory(**subcat_data)
        db.session.add(subcategory)
        db.session.flush()
        categories[subcat_data['slug']] = subcategory
    
    # Create sample resources
    resources_data = [
        {
            'title': 'ISO/IEC 42001:2023 - AI Management Systems Standard',
            'description': 'The complete ISO/IEC 42001:2023 standard document for Artificial Intelligence Management Systems. This comprehensive guide provides requirements for establishing, implementing, maintaining and continually improving an AI management system.',
            'content': 'This standard specifies requirements for an artificial intelligence management system (AIMS) when an organization develops, provides or uses AI systems. It is intended to help organizations develop, provide or use AI systems responsibly in pursuit of their objectives.',
            'resource_type': 'standard',
            'file_format': 'pdf',
            'file_size_bytes': 2457600,  # ~2.4MB
            'author': 'ISO/IEC',
            'version': '2023',
            'category_id': categories['iso-42001-standards'].id,
            'is_public': True,
            'is_featured': True,
            'tags': ['ISO', '42001', 'standard', 'AI management', 'requirements'],
            'keywords': 'ISO 42001, AI management system, artificial intelligence, standard, requirements, implementation',
            'slug': 'iso-42001-2023-standard',
            'order_index': 1
        },
        {
            'title': 'AI Risk Assessment Template',
            'description': 'Comprehensive template for conducting AI risk assessments in accordance with ISO/IEC 42001 requirements. Includes risk identification, analysis, evaluation, and treatment planning.',
            'content': 'This template provides a structured approach to AI risk assessment, covering technical risks, ethical considerations, regulatory compliance, and operational impacts.',
            'resource_type': 'template',
            'file_format': 'xlsx',
            'file_size_bytes': 1024000,  # ~1MB
            'author': 'Qryti Learn Team',
            'version': '2.1',
            'category_id': categories['risk-management'].id,
            'is_public': False,
            'is_featured': True,
            'tags': ['risk assessment', 'template', 'AI risks', 'compliance'],
            'keywords': 'AI risk assessment, risk management, template, ISO 42001, compliance',
            'slug': 'ai-risk-assessment-template',
            'order_index': 1
        },
        {
            'title': 'AI Governance Framework Implementation Guide',
            'description': 'Step-by-step guide for implementing an AI governance framework within your organization. Covers governance structure, roles and responsibilities, decision-making processes, and oversight mechanisms.',
            'content': 'This guide provides practical advice on establishing effective AI governance, including board oversight, executive accountability, and operational governance structures.',
            'resource_type': 'guide',
            'file_format': 'pdf',
            'file_size_bytes': 3145728,  # ~3MB
            'author': 'Dr. Sarah Chen',
            'version': '1.3',
            'category_id': categories['governance-framework'].id,
            'is_public': False,
            'is_featured': True,
            'tags': ['governance', 'framework', 'implementation', 'AI oversight'],
            'keywords': 'AI governance, framework, implementation, oversight, accountability',
            'slug': 'ai-governance-framework-guide',
            'order_index': 1
        },
        {
            'title': 'ISO 42001 Compliance Checklist',
            'description': 'Comprehensive checklist covering all requirements of ISO/IEC 42001. Perfect for self-assessment, internal audits, and preparation for certification audits.',
            'content': 'This checklist breaks down each clause of ISO 42001 into actionable items, with guidance on evidence collection and compliance demonstration.',
            'resource_type': 'checklist',
            'file_format': 'pdf',
            'file_size_bytes': 512000,  # ~512KB
            'author': 'Qryti Compliance Team',
            'version': '1.0',
            'category_id': categories['audit-checklists'].id,
            'is_public': True,
            'is_featured': True,
            'tags': ['checklist', 'compliance', 'audit', 'ISO 42001'],
            'keywords': 'ISO 42001 checklist, compliance audit, self-assessment, certification',
            'slug': 'iso-42001-compliance-checklist',
            'order_index': 1
        },
        {
            'title': 'Healthcare AI Implementation Case Study',
            'description': 'Detailed case study of a healthcare organization implementing ISO/IEC 42001 for their AI-powered diagnostic systems. Includes challenges, solutions, and lessons learned.',
            'content': 'This case study examines how MedTech Solutions successfully implemented ISO 42001 for their AI diagnostic platform, covering regulatory compliance, risk management, and operational integration.',
            'resource_type': 'case_study',
            'file_format': 'pdf',
            'file_size_bytes': 2048000,  # ~2MB
            'author': 'Dr. Michael Rodriguez',
            'version': '1.0',
            'category_id': categories['case-studies'].id,
            'is_public': False,
            'is_premium': True,
            'tags': ['case study', 'healthcare', 'AI diagnostics', 'implementation'],
            'keywords': 'healthcare AI, case study, implementation, diagnostics, ISO 42001',
            'slug': 'healthcare-ai-case-study',
            'order_index': 1
        },
        {
            'title': 'AI Ethics Training Module',
            'description': 'Interactive training module covering AI ethics principles, bias detection, fairness considerations, and responsible AI development practices.',
            'content': 'This comprehensive training module covers fundamental AI ethics concepts, practical bias mitigation strategies, and ethical decision-making frameworks.',
            'resource_type': 'training',
            'file_format': 'pptx',
            'file_size_bytes': 15728640,  # ~15MB
            'author': 'Prof. Elena Vasquez',
            'version': '2.0',
            'category_id': categories['training-materials'].id,
            'is_public': True,
            'is_featured': False,
            'tags': ['training', 'AI ethics', 'bias', 'fairness', 'responsible AI'],
            'keywords': 'AI ethics training, bias detection, fairness, responsible AI, ethics',
            'slug': 'ai-ethics-training-module',
            'order_index': 2
        },
        {
            'title': 'AI Model Documentation Template',
            'description': 'Standardized template for documenting AI models in compliance with ISO/IEC 42001 requirements. Includes model cards, performance metrics, and risk assessments.',
            'content': 'This template ensures comprehensive documentation of AI models, covering development methodology, training data, performance characteristics, and operational considerations.',
            'resource_type': 'template',
            'file_format': 'docx',
            'file_size_bytes': 768000,  # ~768KB
            'author': 'Qryti Documentation Team',
            'version': '1.2',
            'category_id': categories['templates-checklists'].id,
            'is_public': False,
            'tags': ['template', 'model documentation', 'AI models', 'compliance'],
            'keywords': 'AI model documentation, template, model cards, compliance, ISO 42001',
            'slug': 'ai-model-documentation-template',
            'order_index': 2
        },
        {
            'title': 'Financial Services AI Compliance Guide',
            'description': 'Specialized guide for financial services organizations implementing AI systems under regulatory frameworks including ISO/IEC 42001, Basel III, and MiFID II.',
            'content': 'This guide addresses the unique challenges of AI implementation in financial services, covering regulatory requirements, risk management, and supervisory expectations.',
            'resource_type': 'guide',
            'file_format': 'pdf',
            'file_size_bytes': 4194304,  # ~4MB
            'author': 'Financial AI Consortium',
            'version': '1.1',
            'category_id': categories['implementation-guides'].id,
            'is_public': False,
            'is_premium': True,
            'tags': ['financial services', 'compliance', 'regulation', 'Basel III', 'MiFID II'],
            'keywords': 'financial AI, compliance, regulation, Basel III, MiFID II, ISO 42001',
            'slug': 'financial-ai-compliance-guide',
            'order_index': 3
        },
        {
            'title': 'AI Risk Register Template',
            'description': 'Excel-based risk register template specifically designed for AI systems. Includes risk categories, assessment criteria, and mitigation tracking.',
            'content': 'This comprehensive risk register template helps organizations systematically identify, assess, and manage AI-related risks throughout the system lifecycle.',
            'resource_type': 'template',
            'file_format': 'xlsx',
            'file_size_bytes': 1536000,  # ~1.5MB
            'author': 'Risk Management Institute',
            'version': '3.0',
            'category_id': categories['risk-management'].id,
            'is_public': True,
            'tags': ['risk register', 'template', 'risk management', 'AI risks'],
            'keywords': 'AI risk register, risk management, template, risk assessment, mitigation',
            'slug': 'ai-risk-register-template',
            'order_index': 2
        },
        {
            'title': 'AI Audit Preparation Toolkit',
            'description': 'Complete toolkit for preparing for ISO/IEC 42001 certification audits. Includes document templates, evidence collection guides, and audit simulation exercises.',
            'content': 'This toolkit provides everything needed to prepare for a successful ISO 42001 audit, from documentation preparation to audit simulation and corrective action planning.',
            'resource_type': 'toolkit',
            'file_format': 'zip',
            'file_size_bytes': 10485760,  # ~10MB
            'author': 'Audit Excellence Group',
            'version': '2.2',
            'category_id': categories['audit-checklists'].id,
            'is_public': False,
            'is_premium': True,
            'tags': ['audit', 'toolkit', 'certification', 'preparation', 'ISO 42001'],
            'keywords': 'ISO 42001 audit, certification, audit preparation, toolkit, compliance',
            'slug': 'ai-audit-preparation-toolkit',
            'order_index': 1
        }
    ]
    
    resources = []
    for res_data in resources_data:
        # Convert tags list to JSON
        tags = res_data.pop('tags', [])
        resource = KnowledgeResource(**res_data)
        resource.tags = tags
        resource.published_at = datetime.utcnow() - timedelta(days=30)
        
        db.session.add(resource)
        db.session.flush()
        resources.append(resource)
    
    # Add some download and rating data
    for i, resource in enumerate(resources):
        # Add download counts
        resource.download_count = max(10, (len(resources) - i) * 15 + (i * 7))
        resource.view_count = resource.download_count * 3
        
        # Add ratings
        if i < 7:  # Rate first 7 resources
            rating_count = min(5, i + 2)
            total_rating = rating_count * (4 + (i % 2))  # Ratings between 4-5
            resource.rating_count = rating_count
            resource.rating_sum = total_rating
    
    db.session.commit()
    print(f"Created {len(categories_data) + len(subcategories_data)} categories")
    print(f"Created {len(resources_data)} knowledge base resources")

def main():
    """Main function to create sample data"""
    app = create_app('development')
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            
            # Check if data already exists
            existing_categories = ResourceCategory.query.count()
            if existing_categories > 0:
                print(f"Knowledge base data already exists ({existing_categories} categories found)")
                return
            
            print("Creating sample knowledge base data...")
            create_sample_knowledge_base_data()
            print("Sample knowledge base data created successfully!")
            
        except Exception as e:
            print(f"Error creating sample data: {e}")
            db.session.rollback()

if __name__ == '__main__':
    main()

