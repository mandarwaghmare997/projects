import React, { useState } from 'react';
import LoginForm from '../components/auth/LoginForm';
import RegisterForm from '../components/auth/RegisterForm';

const AuthPage = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);

  const handleSwitchToRegister = () => {
    setIsLogin(false);
  };

  const handleSwitchToLogin = () => {
    setIsLogin(true);
  };

  const handleAuthSuccess = () => {
    if (onAuthSuccess) {
      onAuthSuccess();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {isLogin ? (
          <LoginForm 
            onSwitchToRegister={handleSwitchToRegister}
            onLoginSuccess={handleAuthSuccess}
          />
        ) : (
          <RegisterForm 
            onSwitchToLogin={handleSwitchToLogin}
            onRegisterSuccess={handleAuthSuccess}
          />
        )}
      </div>
    </div>
  );
};

export default AuthPage;

