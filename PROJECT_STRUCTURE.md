# Qryti Learn - Project Structure

```
qryti-learn/
├── README.md                 # Main project documentation
├── ARCHITECTURE.md          # Technical architecture document
├── PROJECT_STRUCTURE.md     # This file
├── .gitignore              # Git ignore rules
├── docker-compose.yml      # Docker configuration (future)
│
├── frontend/               # React.js Frontend Application
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── manifest.json
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   │   ├── common/     # Common components (Header, Footer, etc.)
│   │   │   ├── course/     # Course-related components
│   │   │   ├── quiz/       # Quiz components
│   │   │   ├── auth/       # Authentication components
│   │   │   └── dashboard/  # Dashboard components
│   │   ├── pages/          # Page components
│   │   │   ├── Home.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Courses.jsx
│   │   │   ├── Quiz.jsx
│   │   │   └── Profile.jsx
│   │   ├── hooks/          # Custom React hooks
│   │   │   ├── useAuth.js
│   │   │   ├── useApi.js
│   │   │   └── useProgress.js
│   │   ├── contexts/       # React contexts
│   │   │   ├── AuthContext.jsx
│   │   │   └── ThemeContext.jsx
│   │   ├── utils/          # Utility functions
│   │   │   ├── api.js
│   │   │   ├── auth.js
│   │   │   └── helpers.js
│   │   ├── types/          # TypeScript type definitions
│   │   │   ├── auth.ts
│   │   │   ├── course.ts
│   │   │   └── quiz.ts
│   │   ├── styles/         # CSS and styling
│   │   │   ├── globals.css
│   │   │   └── components.css
│   │   ├── App.jsx         # Main App component
│   │   └── index.js        # Entry point
│   ├── package.json        # Frontend dependencies
│   ├── package-lock.json
│   ├── vite.config.js      # Vite configuration
│   └── tailwind.config.js  # Tailwind CSS configuration
│
├── backend/                # Flask Backend API
│   ├── app/
│   │   ├── __init__.py     # Flask app factory
│   │   ├── models/         # Database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── course.py
│   │   │   ├── quiz.py
│   │   │   ├── progress.py
│   │   │   └── certificate.py
│   │   ├── routes/         # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── courses.py
│   │   │   ├── quizzes.py
│   │   │   ├── progress.py
│   │   │   └── admin.py
│   │   ├── utils/          # Utility functions
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── email.py
│   │   │   ├── certificates.py
│   │   │   └── validators.py
│   │   ├── templates/      # Email templates
│   │   │   ├── welcome.html
│   │   │   └── certificate.html
│   │   └── config.py       # Configuration settings
│   ├── migrations/         # Database migrations
│   ├── static/            # Static files (uploads, certificates)
│   │   ├── certificates/
│   │   └── uploads/
│   ├── uploads/           # User uploaded files
│   ├── requirements.txt   # Python dependencies
│   ├── run.py            # Application entry point
│   └── config.py         # Configuration file
│
├── docs/                  # Documentation
│   ├── API.md            # API documentation
│   ├── DEPLOYMENT.md     # Deployment guide
│   ├── USER_GUIDE.md     # User guide
│   └── ADMIN_GUIDE.md    # Admin guide
│
├── assets/               # Static assets
│   ├── images/          # Images and logos
│   ├── videos/          # Sample videos (if any)
│   └── templates/       # Certificate templates
│
└── scripts/             # Utility scripts
    ├── setup.sh         # Setup script
    ├── deploy.sh        # Deployment script
    └── seed_data.py     # Database seeding script
```

## Key Directories Explained

### Frontend (`/frontend`)
- **React.js application** with modern component architecture
- **Vite** for fast development and building
- **Tailwind CSS** for responsive styling
- **Component-based structure** for maintainability

### Backend (`/backend`)
- **Flask application** with blueprint-based routing
- **SQLAlchemy ORM** for database operations
- **JWT authentication** for secure API access
- **Modular structure** for scalability

### Documentation (`/docs`)
- Comprehensive documentation for users, admins, and developers
- API documentation with examples
- Deployment and setup guides

### Assets (`/assets`)
- Static assets like images, logos, and templates
- Certificate templates for PDF generation
- Brand assets and media files

## Development Workflow

1. **Backend Development**: Start with Flask API and database models
2. **Frontend Development**: Build React components and pages
3. **Integration**: Connect frontend to backend APIs
4. **Testing**: Unit tests and integration tests
5. **Deployment**: Production deployment and monitoring

## Getting Started

1. Clone the repository
2. Set up backend: `cd backend && pip install -r requirements.txt`
3. Set up frontend: `cd frontend && npm install`
4. Run backend: `python run.py`
5. Run frontend: `npm run dev`
6. Access application at `http://localhost:3000`

This structure provides a solid foundation for building, maintaining, and scaling the Qryti Learn LMS platform.

