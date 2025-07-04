import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ProfileForm from '../components/auth/ProfileForm';
import { Button } from '../components/ui/button';
import { ArrowLeft, User } from 'lucide-react';

const ProfilePage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => navigate('/dashboard')}
                className="mr-4"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
              <div className="flex items-center">
                <img 
                  src="/src/assets/qryti-logo.png" 
                  alt="Qryti" 
                  className="h-8 w-auto"
                />
                <h1 className="ml-4 text-xl font-semibold text-gray-900">
                  Profile Settings
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <User className="h-5 w-5 text-gray-400" />
              <span className="text-sm text-gray-700">
                {user?.first_name} {user?.last_name}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8">
        <ProfileForm />
      </main>
    </div>
  );
};

export default ProfilePage;

