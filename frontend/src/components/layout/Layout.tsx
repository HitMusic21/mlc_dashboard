import React, { Suspense } from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { useSidebar } from '../../store/uiStore';
import type { UserResponse } from '../../types/api';

interface LayoutProps {
  children: React.ReactNode;
  user: UserResponse | null;
  onLogout: () => void;
  className?: string;
}

// Error Boundary Component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error boundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="error-boundary">
            <div className="error-content">
              <svg
                className="error-icon"
                width="64"
                height="64"
                viewBox="0 0 64 64"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <circle
                  cx="32"
                  cy="32"
                  r="30"
                  stroke="currentColor"
                  strokeWidth="2"
                />
                <path
                  d="M32 20v16M32 44v2"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
              <h2 className="error-title">Something went wrong</h2>
              <p className="error-message">
                {this.state.error?.message || 'An unexpected error occurred'}
              </p>
              <button
                type="button"
                className="error-button"
                onClick={() => window.location.reload()}
              >
                Reload Page
              </button>
            </div>
          </div>
        )
      );
    }

    return this.props.children;
  }
}

// Loading Fallback Component
const LoadingFallback: React.FC = () => (
  <div className="loading-fallback">
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
      <p className="loading-text">Loading...</p>
    </div>
  </div>
);

export const Layout: React.FC<LayoutProps> = ({
  children,
  user,
  onLogout,
  className = '',
}) => {
  const { isOpen, toggle } = useSidebar();

  return (
    <div className={`app-layout ${className}`}>
      <Header user={user} onLogout={onLogout} />

      <div className="layout-container">
        <Sidebar
          isOpen={isOpen}
          onToggle={toggle}
          userRole={user?.role}
        />

        <main className="layout-main">
          <ErrorBoundary>
            <Suspense fallback={<LoadingFallback />}>{children}</Suspense>
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
};
