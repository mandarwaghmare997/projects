# Qryti Learn - ISO/IEC 42001 AI Management Systems Certification Platform

![Qryti Learn](https://img.shields.io/badge/Qryti-Learn-blue?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-2.0.0-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)

## 🎯 **Overview**

Qryti Learn is a comprehensive e-learning platform specializing in ISO/IEC 42001 AI Management Systems certification. The platform provides interactive courses, assessments, progress tracking, and professional certification with advanced analytics and achievement systems.

### ✨ **Key Features**

- 🎓 **Interactive Learning Modules** - Comprehensive ISO/IEC 42001 curriculum
- 📊 **Advanced Analytics Dashboard** - Real-time learning insights and progress tracking
- 🏆 **Achievement System** - Gamified learning experience with badges and milestones
- 📜 **Professional Certification** - PDF certificate generation with verification
- 🔐 **Secure Authentication** - JWT-based user management and session handling
- 📱 **Responsive Design** - Mobile-friendly interface for learning on any device
- 🔍 **Certificate Verification** - Public verification system with QR codes
- 📈 **Progress Tracking** - Detailed learning analytics and performance metrics

## 🏗️ **Architecture**

### **Technology Stack**

#### Backend
- **Framework:** Flask (Python 3.11)
- **Database:** SQLite (Development) / PostgreSQL (Production)
- **Authentication:** JWT (JSON Web Tokens)
- **PDF Generation:** ReportLab
- **API Documentation:** Built-in Flask routes

#### Frontend
- **Framework:** React 19.1.0 with Vite
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **Charts:** Recharts
- **Routing:** React Router DOM

#### Infrastructure
- **Containerization:** Docker & Docker Compose
- **Web Server:** Nginx (Production)
- **Deployment:** Automated deployment scripts

### **System Components**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (React)       │◄──►│   (Flask)       │◄──►│   (SQLite/PG)   │
│   Port: 80      │    │   Port: 5000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   Certificate   │◄─────────────┘
                        │   Generator     │
                        │   (ReportLab)   │
                        └─────────────────┘
```

## 🚀 **Quick Start**

### **Prerequisites**

- Docker 20.0+
- Docker Compose 2.0+
- Git

### **Installation**

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd qryti-learn
   ```

2. **Deploy with Docker:**
   ```bash
   ./deploy.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:5000
   - Health Check: http://localhost:5000/health

### **Manual Development Setup**

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m src.main
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 📚 **API Documentation**

### **Authentication Endpoints**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/logout` - User logout

### **Course Management**
- `GET /api/courses` - List all courses
- `GET /api/courses/{id}` - Get course details
- `POST /api/courses/{id}/enroll` - Enroll in course

### **Quiz System**
- `GET /api/quizzes` - List available quizzes
- `GET /api/quizzes/{id}` - Get quiz details
- `POST /api/quizzes/{id}/start` - Start quiz attempt
- `POST /api/quizzes/{id}/submit` - Submit quiz answers

### **Certificate System**
- `GET /api/certificates` - List user certificates
- `POST /api/certificates/generate` - Generate certificate
- `GET /api/certificates/verify/{id}` - Verify certificate (public)
- `GET /api/certificates/stats` - Certificate statistics

### **Analytics & Progress**
- `GET /api/analytics/summary` - Analytics dashboard data
- `GET /api/progress/dashboard` - Progress tracking data
- `GET /api/progress/achievements` - User achievements

## 🎓 **Features Deep Dive**

### **Certificate System**
- **Professional PDF Generation:** High-quality certificates with Qryti branding
- **Verification System:** Public verification with unique certificate IDs
- **Security:** Tamper-proof certificates with verification codes
- **Storage:** Secure certificate storage and retrieval

### **Analytics Dashboard**
- **Learning Patterns:** Visual analysis of study habits and progress
- **Performance Metrics:** Detailed scoring and improvement tracking
- **Time Analytics:** Study time tracking and optimization insights
- **Progress Visualization:** Interactive charts and progress indicators

### **Achievement System**
- **Badges & Milestones:** Gamified learning experience
- **Progress Tracking:** Achievement progress and completion status
- **Motivation:** Reward-based learning encouragement
- **Social Features:** Achievement sharing and recognition

### **Progress Tracking**
- **Real-time Updates:** Live progress monitoring
- **Course Completion:** Module and course completion tracking
- **Performance Analytics:** Detailed performance insights
- **Learning Path:** Personalized learning recommendations

## 🔧 **Configuration**

### **Environment Variables**

Create a `.env` file in the project root:

```env
# Security
JWT_SECRET_KEY=your-super-secret-jwt-key

# Database
DATABASE_URL=sqlite:///src/database/app.db
POSTGRES_PASSWORD=your-secure-database-password

# Application
FLASK_ENV=production
CORS_ORIGINS=https://qryti.com,https://www.qryti.com

# Optional: External Services
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=qryti-certificates
```

### **Docker Configuration**

The application uses Docker Compose for orchestration:

- **Backend:** Flask API server with health checks
- **Frontend:** Nginx-served React application
- **Database:** SQLite (development) or PostgreSQL (production)
- **Networking:** Internal Docker network for service communication

## 📊 **Database Schema**

### **Core Models**

- **Users:** User accounts and authentication
- **Courses:** Course content and structure
- **Modules:** Course modules and lessons
- **Quizzes:** Assessments and evaluations
- **Questions:** Quiz questions and answers
- **Certificates:** Generated certificates and verification
- **Progress:** User progress and completion tracking
- **Achievements:** Gamification and milestone tracking

### **Relationships**

```
Users ──┬── Enrollments ── Courses
        ├── Progress ──── Modules
        ├── QuizAttempts ── Quizzes
        ├── Certificates
        └── Achievements
```

## 🧪 **Testing**

### **Backend Testing**
```bash
cd backend
python test_certificate_generator.py
```

### **Frontend Testing**
```bash
cd frontend
npm test
```

### **Integration Testing**
```bash
./deploy.sh
curl http://localhost:5000/health
curl http://localhost/health
```

## 🚀 **Deployment**

### **Production Deployment**

1. **Prepare Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Deploy:**
   ```bash
   ./deploy.sh
   ```

3. **Verify Deployment:**
   ```bash
   ./deploy.sh status
   ```

### **Deployment Commands**

- `./deploy.sh` - Full deployment
- `./deploy.sh stop` - Stop services
- `./deploy.sh restart` - Restart services
- `./deploy.sh logs` - View logs
- `./deploy.sh status` - Check status
- `./deploy.sh clean` - Clean up

### **AWS Deployment**

For AWS deployment, the application is designed to be:
- **Lightweight:** Minimal resource requirements
- **Loosely Coupled:** Microservices architecture
- **AWS Compatible:** Ready for ECS, EKS, or EC2 deployment
- **Tagged:** All resources tagged with 'Qryti.com' domain

## 📈 **Performance**

### **Benchmarks**
- **API Response Time:** < 200ms average
- **Certificate Generation:** < 1 second
- **Database Queries:** < 50ms average
- **Frontend Load Time:** < 2 seconds

### **Scalability**
- **Horizontal Scaling:** Docker container orchestration
- **Database Scaling:** PostgreSQL with read replicas
- **CDN Integration:** Static asset optimization
- **Caching:** Redis integration ready

## 🔒 **Security**

### **Authentication & Authorization**
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- Secure password hashing with bcrypt
- Session management and timeout

### **Data Protection**
- HTTPS enforcement in production
- SQL injection prevention with ORM
- XSS protection with content security policy
- CORS configuration for API security

### **Certificate Security**
- Tamper-proof PDF certificates
- Unique verification codes
- Public verification system
- Secure certificate storage

## 🤝 **Contributing**

### **Development Workflow**

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit a pull request

### **Code Standards**

- **Python:** PEP 8 compliance
- **JavaScript:** ESLint configuration
- **Documentation:** Comprehensive inline comments
- **Testing:** Unit and integration tests required

## 📞 **Support**

### **Documentation**
- API Documentation: `/docs` endpoint
- User Guide: Available in the application
- Developer Guide: This README

### **Contact**
- **Website:** https://qryti.com
- **Email:** support@qryti.com
- **Documentation:** https://docs.qryti.com

## 📄 **License**

This project is proprietary software owned by Qryti. All rights reserved.

## 🎉 **Acknowledgments**

- ISO/IEC 42001 standard for AI management systems
- Open source libraries and frameworks used
- Development team and contributors

---

**Version:** 2.0.0 (Phase 6 - Certification System)  
**Last Updated:** July 4, 2025  
**Status:** Production Ready  

For the latest updates and documentation, visit [qryti.com](https://qryti.com)

