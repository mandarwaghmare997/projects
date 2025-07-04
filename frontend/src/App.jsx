import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  BookOpen, 
  Video, 
  Award, 
  Users, 
  BarChart3, 
  Shield, 
  CheckCircle, 
  PlayCircle,
  Download,
  Star,
  ArrowRight,
  Brain,
  Target,
  Zap,
  Globe,
  Clock
} from 'lucide-react'
import './App.css'

function App() {
  const [animatedStats, setAnimatedStats] = useState({
    students: 0,
    courses: 0,
    certificates: 0,
    satisfaction: 0
  })

  const [currentTestimonial, setCurrentTestimonial] = useState(0)

  const finalStats = {
    students: 2500,
    courses: 12,
    certificates: 1800,
    satisfaction: 98
  }

  const testimonials = [
    {
      name: "Sarah Chen",
      role: "AI Governance Manager",
      company: "TechCorp Inc.",
      content: "Qryti Learn transformed our understanding of ISO 42001. The structured approach and practical examples made complex concepts accessible.",
      rating: 5
    },
    {
      name: "Michael Rodriguez",
      role: "Compliance Director",
      company: "FinanceAI Solutions",
      content: "The certification levels are perfectly designed. We went from foundations to lead implementer in just 3 months.",
      rating: 5
    },
    {
      name: "Dr. Emily Watson",
      role: "Chief Data Officer",
      company: "HealthTech Innovations",
      content: "Outstanding platform! The video modules and knowledge base are comprehensive. Highly recommend for any AI-focused organization.",
      rating: 5
    }
  ]

  const certificationLevels = [
    {
      level: 1,
      title: "ISO 42001 Foundations",
      description: "Basic understanding of AI governance and ISO 42001 standard",
      duration: "2-3 hours",
      modules: 6,
      color: "bg-blue-500"
    },
    {
      level: 2,
      title: "ISO 42001 Practitioner",
      description: "Practical implementation knowledge and risk management",
      duration: "4-5 hours",
      modules: 8,
      color: "bg-green-500"
    },
    {
      level: 3,
      title: "ISO 42001 Lead Implementer",
      description: "Advanced implementation strategies and audit preparation",
      duration: "6-8 hours",
      modules: 10,
      color: "bg-orange-500"
    },
    {
      level: 4,
      title: "ISO 42001 Auditor/Assessor",
      description: "Audit techniques and assessment methodologies",
      duration: "8-10 hours",
      modules: 12,
      color: "bg-purple-500"
    }
  ]

  const features = [
    {
      icon: Video,
      title: "Video Modules",
      description: "Curated video lessons aligned with ISO 42001 clauses and real-world AI governance scenarios"
    },
    {
      icon: BookOpen,
      title: "Knowledge Base",
      description: "Downloadable templates, best practices, and regulation mappings (GDPR, NIST AI RMF, OECD)"
    },
    {
      icon: Target,
      title: "Quizzes & Exams",
      description: "Timed assessments, MCQs, case-based questions, and practical application scenarios"
    },
    {
      icon: Award,
      title: "Digital Certificates",
      description: "Shareable, verifiable digital certificates with Certificate ID and verification link"
    },
    {
      icon: BarChart3,
      title: "Progress Tracking",
      description: "User dashboard to view learning progress, scores, and upcoming modules"
    },
    {
      icon: Users,
      title: "Enterprise Ready",
      description: "Multi-user access, team enrollment, group progress tracking, and compliance reports"
    }
  ]

  // Animate statistics on component mount
  useEffect(() => {
    const duration = 2000 // 2 seconds
    const steps = 60
    const stepDuration = duration / steps

    let currentStep = 0
    const timer = setInterval(() => {
      currentStep++
      const progress = currentStep / steps

      setAnimatedStats({
        students: Math.floor(finalStats.students * progress),
        courses: Math.floor(finalStats.courses * progress),
        certificates: Math.floor(finalStats.certificates * progress),
        satisfaction: Math.floor(finalStats.satisfaction * progress)
      })

      if (currentStep >= steps) {
        clearInterval(timer)
        setAnimatedStats(finalStats)
      }
    }, stepDuration)

    return () => clearInterval(timer)
  }, [])

  // Rotate testimonials
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length)
    }, 5000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Qryti Learn
            </span>
          </div>
          <nav className="hidden md:flex items-center space-x-6">
            <a href="#features" className="text-gray-600 hover:text-blue-600 transition-colors">Features</a>
            <a href="#courses" className="text-gray-600 hover:text-blue-600 transition-colors">Courses</a>
            <a href="#pricing" className="text-gray-600 hover:text-blue-600 transition-colors">Pricing</a>
            <Button variant="outline" className="mr-2">Sign In</Button>
            <Button>Get Started</Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center">
          <Badge className="mb-4 bg-blue-100 text-blue-800 hover:bg-blue-200">
            🚀 New: Level 4 Auditor Certification Available
          </Badge>
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent leading-tight">
            Master ISO/IEC 42001
            <br />
            <span className="text-4xl md:text-5xl">AI Management Systems</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            The only cloud-based Learning Management System designed specifically for ISO/IEC 42001 certification. 
            Learn, assess, and certify with structured, self-paced content from beginner to expert level.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3">
              <PlayCircle className="w-5 h-5 mr-2" />
              Start Learning Free
            </Button>
            <Button size="lg" variant="outline" className="px-8 py-3">
              <Download className="w-5 h-5 mr-2" />
              Download Brochure
            </Button>
          </div>

          {/* Animated Statistics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-blue-600 mb-2">
                {animatedStats.students.toLocaleString()}+
              </div>
              <div className="text-gray-600">Students Enrolled</div>
            </div>
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-green-600 mb-2">
                {animatedStats.courses}
              </div>
              <div className="text-gray-600">Expert Courses</div>
            </div>
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-orange-600 mb-2">
                {animatedStats.certificates.toLocaleString()}+
              </div>
              <div className="text-gray-600">Certificates Issued</div>
            </div>
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-purple-600 mb-2">
                {animatedStats.satisfaction}%
              </div>
              <div className="text-gray-600">Satisfaction Rate</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-white">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Comprehensive Learning Platform</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Everything you need to master ISO/IEC 42001 AI Management Systems in one integrated platform
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-0 shadow-md">
                <CardHeader>
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center mb-4">
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Certification Levels */}
      <section id="courses" className="py-20 px-4 bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Certification Levels</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Progress through multiple certification levels, representing growing expertise in AI governance
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {certificationLevels.map((cert, index) => (
              <Card key={index} className="hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border-0 shadow-lg overflow-hidden">
                <div className={`h-2 ${cert.color}`}></div>
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant="secondary" className="text-xs">Level {cert.level}</Badge>
                    <div className="flex items-center">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                    </div>
                  </div>
                  <CardTitle className="text-lg leading-tight">{cert.title}</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <CardDescription className="text-gray-600 mb-4 leading-relaxed">
                    {cert.description}
                  </CardDescription>
                  <div className="space-y-2 text-sm text-gray-500">
                    <div className="flex items-center">
                      <Video className="w-4 h-4 mr-2" />
                      {cert.modules} modules
                    </div>
                    <div className="flex items-center">
                      <Clock className="w-4 h-4 mr-2" />
                      {cert.duration}
                    </div>
                  </div>
                  <Button className="w-full mt-4" variant="outline">
                    Start Level {cert.level}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-4 bg-white">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">What Our Students Say</h2>
            <p className="text-xl text-gray-600">Join thousands of professionals who have advanced their AI governance expertise</p>
          </div>
          <div className="max-w-4xl mx-auto">
            <Card className="border-0 shadow-xl">
              <CardContent className="p-8">
                <div className="text-center">
                  <div className="flex justify-center mb-4">
                    {[...Array(testimonials[currentTestimonial].rating)].map((_, i) => (
                      <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <blockquote className="text-xl text-gray-700 mb-6 italic leading-relaxed">
                    "{testimonials[currentTestimonial].content}"
                  </blockquote>
                  <div>
                    <div className="font-semibold text-lg">{testimonials[currentTestimonial].name}</div>
                    <div className="text-gray-600">{testimonials[currentTestimonial].role}</div>
                    <div className="text-blue-600 font-medium">{testimonials[currentTestimonial].company}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <div className="flex justify-center mt-6 space-x-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  className={`w-3 h-3 rounded-full transition-colors ${
                    index === currentTestimonial ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                  onClick={() => setCurrentTestimonial(index)}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="container mx-auto text-center">
          <h2 className="text-4xl font-bold mb-4">Ready to Master AI Governance?</h2>
          <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
            Join the leading professionals who trust Qryti Learn for their ISO/IEC 42001 certification journey
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3">
              <Zap className="w-5 h-5 mr-2" />
              Start Free Trial
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600 px-8 py-3">
              <Globe className="w-5 h-5 mr-2" />
              Enterprise Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold">Qryti Learn</span>
              </div>
              <p className="text-gray-400 leading-relaxed">
                The premier platform for ISO/IEC 42001 AI Management Systems certification and training.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Platform</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Courses</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Certifications</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Knowledge Base</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Progress Tracking</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Community</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Enterprise</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 Qryti Learn. All rights reserved. Built for the future of AI governance.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App

