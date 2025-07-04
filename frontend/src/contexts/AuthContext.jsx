import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import apiService from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const refreshIntervalRef = useRef(null);

  // Initialize authentication state
  useEffect(() => {
    initializeAuth();
    
    // Cleanup on unmount
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, []);

  // Set up automatic token refresh
  const setupTokenRefresh = () => {
    // Clear existing interval
    if (refreshIntervalRef.current) {
      clearInterval(refreshIntervalRef.current);
    }

    // Refresh token every 14 minutes (tokens expire in 15 minutes)
    refreshIntervalRef.current = setInterval(async () => {
      try {
        if (apiService.isAuthenticated()) {
          await apiService.refreshToken();
        }
      } catch (error) {
        console.error('Automatic token refresh failed:', error);
        // If refresh fails, logout user
        await logout();
      }
    }, 14 * 60 * 1000); // 14 minutes
  };

  const initializeAuth = async () => {
    try {
      if (apiService.isAuthenticated()) {
        const profileData = await apiService.getProfile();
        setUser(profileData.user);
        setupTokenRefresh();
      }
    } catch (error) {
      console.error('Failed to initialize auth:', error);
      // Clear invalid tokens
      apiService.setToken(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.login(credentials);
      setUser(response.user);
      setupTokenRefresh();
      
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.register(userData);
      setUser(response.user);
      setupTokenRefresh();
      
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      // Clear token refresh interval
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
        refreshIntervalRef.current = null;
      }
      
      await apiService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setError(null);
    }
  };

  const updateUser = (userData) => {
    setUser(userData);
  };

  const updateProfile = async (profileData) => {
    try {
      setError(null);
      const response = await apiService.updateProfile(profileData);
      setUser(response.user);
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    }
  };

  const changePassword = async (passwordData) => {
    try {
      setError(null);
      return await apiService.changePassword(passwordData);
    } catch (error) {
      setError(error.message);
      throw error;
    }
  };

  const clearError = () => {
    setError(null);
  };

  const value = {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    updateUser,
    updateProfile,
    changePassword,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

