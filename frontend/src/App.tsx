import React, { useEffect, Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { Login } from './pages/Login';
import { ToastContainer } from './components/ui';
import { ToastProvider } from './components/notifications/ToastContainer';
import { useAuthStore } from './store/authStore';
import { usePreferencesStore } from './stores/usePreferencesStore';
import type { UserResponse } from './types/api';

// Lazy load pages for code splitting
const Dashboard = lazy(() => import('./pages/Dashboard').then(m => ({ default: m.Dashboard })));
const WorksBrowser = lazy(() => import('./pages/WorksBrowser').then(m => ({ default: m.WorksBrowser })));
const CatalogMatcher = lazy(() => import('./pages/CatalogMatcher').then(m => ({ default: m.CatalogMatcher })));
const ResultsViewer = lazy(() => import('./pages/ResultsViewer').then(m => ({ default: m.ResultsViewer })));
const NotificationsPage = lazy(() => import('./pages/NotificationsPage').then(m => ({ default: m.NotificationsPage })));
const SavedSearches = lazy(() => import('./pages/SavedSearches'));
const Admin = lazy(() => import('./pages/Admin').then(m => ({ default: m.Admin })));

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Protected Route Component
interface ProtectedRouteProps {
  children: React.ReactNode;
  user: UserResponse | null;
  requiredRole?: 'admin';
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  user,
  requiredRole,
}) => {
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

function App() {
  const { user, isLoading, checkAuth, logout } = useAuthStore();
  const { preferences, fetchPreferences } = usePreferencesStore();

  // Check authentication on mount
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Fetch preferences when user is authenticated
  useEffect(() => {
    if (user) {
      fetchPreferences().catch((error) => {
        console.error('Failed to fetch user preferences:', error);
      });
    }
  }, [user, fetchPreferences]);

  // Apply theme from preferences
  useEffect(() => {
    if (preferences?.theme) {
      const theme = preferences.theme;

      if (theme === 'auto') {
        // Use system preference
        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
      } else {
        document.documentElement.setAttribute('data-theme', theme);
      }
    }
  }, [preferences?.theme]);

  const handleLogout = async () => {
    await logout();
    window.location.href = '/login';
  };

  if (isLoading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner">
          <svg
            className="spinner-icon"
            width="48"
            height="48"
            viewBox="0 0 48 48"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle
              cx="24"
              cy="24"
              r="20"
              stroke="currentColor"
              strokeWidth="4"
              opacity="0.25"
            />
            <path
              d="M24 4a20 20 0 0120 20"
              stroke="currentColor"
              strokeWidth="4"
              strokeLinecap="round"
            />
          </svg>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <BrowserRouter>
          <ToastContainer />
        <Routes>
          {/* Public Routes */}
          <Route
            path="/login"
            element={
              user ? (
                <Navigate to="/" replace />
              ) : (
                <Login />
              )
            }
          />

          {/* Protected Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute user={user}>
                <Layout user={user} onLogout={handleLogout}>
                  <Suspense fallback={<div className="page-loading">Loading...</div>}>
                    <Dashboard />
                  </Suspense>
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/works"
            element={
              <ProtectedRoute user={user}>
                <Layout user={user} onLogout={handleLogout}>
                  <Suspense fallback={<div className="page-loading">Loading...</div>}>
                    <WorksBrowser />
                  </Suspense>
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/catalog"
            element={
              <ProtectedRoute user={user}>
                <Layout user={user} onLogout={handleLogout}>
                  <Suspense fallback={<div className="page-loading">Loading...</div>}>
                    <CatalogMatcher />
                  </Suspense>
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/results/:uploadId"
            element={
              <ProtectedRoute user={user}>
                <Layout user={user} onLogout={handleLogout}>
                  <Suspense fallback={<div className="page-loading">Loading...</div>}>
                    <ResultsViewer />
                  </Suspense>
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/notifications"
            element={
              <ProtectedRoute user={user}>
                <Layout user={user} onLogout={handleLogout}>
                  <Suspense fallback={<div className="page-loading">Loading...</div>}>
                    <NotificationsPage />
                  </Suspense>
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/saved-searches"
            element={
              <ProtectedRoute user={user}>
                <Layout user={user} onLogout={handleLogout}>
                  <Suspense fallback={<div className="page-loading">Loading...</div>}>
                    <SavedSearches />
                  </Suspense>
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Admin Routes */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute user={user} requiredRole="admin">
                <Layout user={user} onLogout={handleLogout}>
                  <Suspense fallback={<div className="page-loading">Loading...</div>}>
                    <Admin />
                  </Suspense>
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* 404 Not Found */}
          <Route
            path="*"
            element={
              <div className="not-found-page">
                <h1>404 - Page Not Found</h1>
                <p>The page you're looking for doesn't exist.</p>
                <a href="/">Go to Dashboard</a>
              </div>
            }
          />
        </Routes>
        </BrowserRouter>
      </ToastProvider>
    </QueryClientProvider>
  );
}

export default App;
