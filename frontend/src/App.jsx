import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

import { useAuthStore } from './store/authStore';
import { useThemeStore } from './store/themeStore';

import LoginForm from './components/LoginForm';
import Dashboard from './components/Dashboard';
import AdminPanel from './components/AdminPanel';
import NotFound from './pages/NotFound';
import LandingPage from './components/LandingPage';

function App() {
  const { isAuthenticated, user } = useAuthStore();
  const { isDark } = useThemeStore();

  return (
    <div className={isDark ? 'dark' : ''}>
      <Router>
        <div className="min-h-screen bg-dark-bg text-dark-text-primary">
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<LandingPage />} />
            <Route 
              path="/login" 
              element={
                isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginForm />
              } 
            />
            
            {/* Protected Routes */}
            <Route 
              path="/dashboard" 
              element={
                isAuthenticated ? <Dashboard /> : <Navigate to="/login" replace />
              } 
            />
            
            {/* Admin Routes */}
            <Route 
              path="/admin" 
              element={
                isAuthenticated && user?.role === 'admin' 
                  ? <AdminPanel /> 
                  : <Navigate to="/dashboard" replace />
              } 
            />
            
            {/* 404 */}
            <Route path="*" element={<NotFound />} />
          </Routes>
          
          <Toaster 
            position="top-right"
            toastOptions={{
              className: 'dark:bg-dark-card dark:text-dark-text-primary',
              duration: 4000,
            }}
          />
        </div>
      </Router>
    </div>
  );
}

export default App;