# Qryti Learn - Technical Architecture

## Project Overview
Qryti Learn is a cloud-based Learning Management System (LMS) designed specifically for ISO/IEC 42001 AI Management Systems certification. The platform provides structured, self-paced learning with video modules, quizzes, certifications, and enterprise features.

## Technology Stack

### Frontend
- **Framework**: React.js 18+ with TypeScript
- **Styling**: Tailwind CSS for responsive design
- **State Management**: React Context API + useReducer
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **UI Components**: Custom components with modern design
- **Icons**: Lucide React icons

### Backend
- **Framework**: Flask (Python 3.11+)
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy
- **Authentication**: JWT tokens with Flask-JWT-Extended
- **API**: RESTful API with JSON responses
- **File Storage**: Local filesystem (development) / Cloud storage (production)
- **Email**: Flask-Mail for notifications

### Development Tools
- **Package Managers**: npm (frontend), pip (backend)
- **Build Tools**: Vite (React), Flask development server
- **Version Control**: Git with GitHub
- **Documentation**: Markdown files

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React.js      │    │   Flask API     │    │   SQLite DB     │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   YouTube       │    │   File System   │    │   Certificate   │
│   Videos        │    │   (Knowledge    │    │   Generator     │
│                 │    │    Base)        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Database Schema

### Users Table
- id (Primary Key)
- email (Unique)
- password_hash
- first_name
- last_name
- organization
- role (student, admin, enterprise_admin)
- created_at
- updated_at
- is_active

### Courses Table
- id (Primary Key)
- title
- description
- level (1-4: Foundations, Practitioner, Lead Implementer, Auditor)
- duration_hours
- is_active
- created_at
- updated_at

### Modules Table
- id (Primary Key)
- course_id (Foreign Key)
- title
- description
- video_url (YouTube)
- content_text
- order_index
- is_active

### Quizzes Table
- id (Primary Key)
- module_id (Foreign Key)
- title
- description
- time_limit_minutes
- passing_score
- is_active

### Questions Table
- id (Primary Key)
- quiz_id (Foreign Key)
- question_text
- question_type (mcq, multiple_select, case_study)
- options (JSON)
- correct_answers (JSON)
- explanation
- points

### User_Progress Table
- id (Primary Key)
- user_id (Foreign Key)
- course_id (Foreign Key)
- module_id (Foreign Key)
- status (not_started, in_progress, completed)
- score
- completed_at

### Certificates Table
- id (Primary Key)
- user_id (Foreign Key)
- course_id (Foreign Key)
- certificate_id (Unique)
- issued_at
- verification_url
- pdf_path

### Quiz_Attempts Table
- id (Primary Key)
- user_id (Foreign Key)
- quiz_id (Foreign Key)
- score
- total_questions
- answers (JSON)
- started_at
- completed_at

## API Endpoints

### Authentication
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/profile
- PUT /api/auth/profile

### Courses
- GET /api/courses
- GET /api/courses/{id}
- GET /api/courses/{id}/modules
- POST /api/courses/{id}/enroll

### Modules
- GET /api/modules/{id}
- POST /api/modules/{id}/complete

### Quizzes
- GET /api/quizzes/{id}
- POST /api/quizzes/{id}/attempt
- GET /api/quizzes/{id}/results

### Progress
- GET /api/progress/dashboard
- GET /api/progress/courses
- GET /api/progress/certificates

### Admin
- GET /api/admin/users
- GET /api/admin/analytics
- POST /api/admin/courses
- PUT /api/admin/courses/{id}

## Security Features

### Authentication & Authorization
- JWT token-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Session management
- CORS configuration

### Data Protection
- Input validation and sanitization
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection
- Rate limiting for API endpoints
- Secure file upload handling

## Certification Levels

### Level 1: ISO 42001 Foundations
- Basic understanding of AI governance
- Introduction to ISO 42001 standard
- 4-6 modules, 2-3 hours total
- Basic quiz (20 questions, 70% passing)

### Level 2: ISO 42001 Practitioner
- Practical implementation knowledge
- Risk management and controls
- 6-8 modules, 4-5 hours total
- Intermediate quiz (30 questions, 75% passing)

### Level 3: ISO 42001 Lead Implementer
- Advanced implementation strategies
- Audit preparation and management
- 8-10 modules, 6-8 hours total
- Advanced quiz (40 questions, 80% passing)

### Level 4: ISO 42001 Auditor/Assessor
- Audit techniques and methodologies
- Assessment frameworks
- 10-12 modules, 8-10 hours total
- Expert quiz (50 questions, 85% passing)

## Deployment Strategy

### Development Environment
- Local development with hot reload
- SQLite database for simplicity
- Mock data for testing

### Production Environment
- Cloud deployment (AWS/Azure/GCP)
- PostgreSQL database
- CDN for static assets
- SSL/TLS encryption
- Automated backups

## Performance Considerations

### Frontend Optimization
- Code splitting and lazy loading
- Image optimization
- Caching strategies
- Progressive Web App (PWA) features

### Backend Optimization
- Database indexing
- Query optimization
- Caching (Redis for production)
- API response compression

## Monitoring & Analytics

### User Analytics
- Learning progress tracking
- Quiz performance metrics
- Certification completion rates
- User engagement metrics

### System Monitoring
- API response times
- Error tracking
- Database performance
- User activity logs

## Future Enhancements

### Phase 2 Features
- Mobile app (React Native)
- Advanced analytics dashboard
- Integration with HR systems
- Bulk user management
- Custom branding for enterprises

### Phase 3 Features
- AI-powered learning recommendations
- Adaptive learning paths
- Virtual reality training modules
- Integration with compliance tools
- Multi-language support

This architecture provides a solid foundation for building a scalable, secure, and feature-rich Learning Management System for ISO/IEC 42001 certification.

