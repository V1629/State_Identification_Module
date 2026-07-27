import { createContext, useState, useEffect, useContext } from 'react';
import { authenticateWithGoogle, authenticateWithEmail, registerWithEmail } from '../api/endpoints';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on mount
    const token = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('auth_user');
    
    if (token && storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error('Failed to parse user from local storage');
        logout();
      }
    }
    setLoading(false);
  }, []);

  const _handleAuthSuccess = (data) => {
    const { token, user: userData } = data;
    localStorage.setItem('auth_token', token);
    localStorage.setItem('auth_user', JSON.stringify(userData));
    setUser(userData);
    return userData;
  };

  const loginWithGoogle = async (credential, isSignup = false) => {
    try {
      const data = await authenticateWithGoogle(credential, isSignup);
      return _handleAuthSuccess(data);
    } catch (error) {
      console.error('Google Auth failed:', error);
      throw error;
    }
  };

  const loginWithEmail = async (email, password) => {
    try {
      const data = await authenticateWithEmail(email, password);
      return _handleAuthSuccess(data);
    } catch (error) {
      console.error('Email login failed:', error);
      throw error;
    }
  };

  const register = async (name, email, password) => {
    try {
      const data = await registerWithEmail(name, email, password);
      return _handleAuthSuccess(data);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, loginWithGoogle, loginWithEmail, register, logout }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
