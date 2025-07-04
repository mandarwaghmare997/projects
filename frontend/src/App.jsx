import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import QuizPage from './pages/QuizPage';
import ProfilePage from './pages/ProfilePage';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }
  
  return isAuthenticated ? children : <Navigate to="/auth" replace />;
};

// Public Route Component (redirect to dashboard if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }
  
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children;
};

// Landing Page Component (updated from the original)
const LandingPageComponent = () => {
  const [currentTestimonial, setCurrentTestimonial] = useState(0);

  const testimonials = [
    {
      name: "Sarah Chen",
      role: "AI Ethics Officer",
      company: "TechCorp",
      content: "Qryti Learn provided exactly what I needed to understand ISO 42001. The practical approach and real-world examples made complex concepts accessible.",
      rating: 5
    },
    {
      name: "Michael Rodriguez",
      role: "Compliance Manager",
      company: "DataSafe Inc",
      content: "The certification process was smooth and comprehensive. I now feel confident implementing AI governance frameworks in our organization.",
      rating: 5
    },
    {
      name: "Dr. Emily Watson",
      role: "AI Research Director",
      company: "Innovation Labs",
      content: "Outstanding content quality and expert instruction. This platform sets the standard for AI governance education.",
      rating: 5
    }
  ];

  React.useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <img 
                src="/src/assets/qryti-logo.png" 
                alt="Qryti" 
                className="h-8 w-auto"
              />
            </div>
            <div className="flex items-center space-x-4">
              <a 
                href="/auth" 
                className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Sign In
              </a>
              <a 
                href="/auth" 
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:from-blue-700 hover:to-purple-700 transition-all"
              >
                Get Started
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Master{' '}
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                ISO/IEC 42001
              </span>
              <br />
              AI Management Systems
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Comprehensive certification platform for AI governance professionals. 
              Learn, assess, and certify your expertise in AI management systems with industry-leading content.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a 
                href="/auth"
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all transform hover:scale-105"
              >
                Start Learning Today
              </a>
              <button className="border border-gray-300 text-gray-700 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-50 transition-all">
                View Courses
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Everything You Need to Succeed
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Comprehensive learning platform designed for AI governance professionals
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: "🎥",
                title: "Video Modules",
                description: "Expert-led video lessons aligned with ISO 42001 clauses and real-world scenarios"
              },
              {
                icon: "📚",
                title: "Knowledge Base",
                description: "Downloadable templates, best practices, and regulation mappings"
              },
              {
                icon: "📝",
                title: "Interactive Quizzes",
                description: "Timed assessments with instant feedback and detailed explanations"
              },
              {
                icon: "🏆",
                title: "Digital Certificates",
                description: "Verifiable certificates with unique IDs and professional recognition"
              },
              {
                icon: "📊",
                title: "Progress Tracking",
                description: "Comprehensive dashboard to monitor your learning journey"
              },
              {
                icon: "👥",
                title: "Enterprise Ready",
                description: "Team management and compliance reporting for organizations"
              }
            ].map((feature, index) => (
              <div key={index} className="text-center p-6 rounded-lg hover:shadow-lg transition-shadow">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Certification Levels */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Certification Levels
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Progressive learning path from foundation to expert level
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                level: "Level 1",
                title: "ISO 42001 Foundations",
                description: "Basic understanding of AI governance and ISO 42001 standard",
                duration: "3 hours",
                modules: 4
              },
              {
                level: "Level 2", 
                title: "ISO 42001 Practitioner",
                description: "Practical implementation knowledge and risk management",
                duration: "5 hours",
                modules: 6
              },
              {
                level: "Level 3",
                title: "ISO 42001 Lead Implementer", 
                description: "Advanced implementation strategies and audit preparation",
                duration: "8 hours",
                modules: 8
              },
              {
                level: "Level 4",
                title: "ISO 42001 Auditor/Assessor",
                description: "Audit techniques and assessment methodologies", 
                duration: "10 hours",
                modules: 10
              }
            ].map((cert, index) => (
              <div key={index} className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="text-center mb-4">
                  <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                    {cert.level}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{cert.title}</h3>
                <p className="text-gray-600 text-sm mb-4">{cert.description}</p>
                <div className="flex justify-between text-sm text-gray-500 mb-4">
                  <span>⏱️ {cert.duration}</span>
                  <span>📚 {cert.modules} modules</span>
                </div>
                <a 
                  href="/auth"
                  className="block w-full text-center bg-gradient-to-r from-blue-600 to-purple-600 text-white py-2 rounded-md hover:from-blue-700 hover:to-purple-700 transition-all"
                >
                  Start Course
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              What Our Learners Say
            </h2>
          </div>

          <div className="bg-gray-50 rounded-lg p-8 text-center">
            <div className="mb-6">
              {[...Array(testimonials[currentTestimonial].rating)].map((_, i) => (
                <span key={i} className="text-yellow-400 text-xl">⭐</span>
              ))}
            </div>
            <blockquote className="text-xl text-gray-700 mb-6">
              "{testimonials[currentTestimonial].content}"
            </blockquote>
            <div>
              <div className="font-semibold text-gray-900">
                {testimonials[currentTestimonial].name}
              </div>
              <div className="text-gray-600">
                {testimonials[currentTestimonial].role}, {testimonials[currentTestimonial].company}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Start Your AI Governance Journey?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of professionals advancing their careers with ISO/IEC 42001 certification
          </p>
          <a 
            href="/auth"
            className="bg-white text-blue-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition-all transform hover:scale-105"
          >
            Get Started Today
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <img 
                src="/src/assets/qryti-logo.png" 
                alt="Qryti" 
                className="h-8 w-auto mb-4 filter brightness-0 invert"
              />
              <p className="text-gray-400">
                Leading AI governance education platform for ISO/IEC 42001 certification.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Courses</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Foundations</a></li>
                <li><a href="#" className="hover:text-white">Practitioner</a></li>
                <li><a href="#" className="hover:text-white">Lead Implementer</a></li>
                <li><a href="#" className="hover:text-white">Auditor/Assessor</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Knowledge Base</a></li>
                <li><a href="#" className="hover:text-white">Templates</a></li>
                <li><a href="#" className="hover:text-white">Best Practices</a></li>
                <li><a href="#" className="hover:text-white">Compliance Guides</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Help Center</a></li>
                <li><a href="#" className="hover:text-white">Contact Us</a></li>
                <li><a href="#" className="hover:text-white">Enterprise</a></li>
                <li><a href="#" className="hover:text-white">Verify Certificate</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 Qryti.com. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Main App Component
const AppContent = () => {
  return (
    <Router>
      <Routes>
        <Route 
          path="/" 
          element={
            <PublicRoute>
              <LandingPageComponent />
            </PublicRoute>
          } 
        />
        <Route 
          path="/auth" 
          element={
            <PublicRoute>
              <AuthPage />
            </PublicRoute>
          } 
        />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/profile" 
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/quizzes" 
          element={
            <ProtectedRoute>
              <QuizPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/course/:courseId/quizzes" 
          element={
            <ProtectedRoute>
              <QuizPage />
            </ProtectedRoute>
          } 
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;

