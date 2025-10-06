import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useToast } from '../store/uiStore';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading, error, clearError } = useAuthStore();
  const toast = useToast();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    try {
      await login(email, password);
      toast.success('Successfully logged in!');
      navigate('/');
    } catch (err: any) {
      // Error is already set in the store
      toast.error(error || 'Login failed. Please check your credentials.');
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <svg
            className="login-logo"
            width="48"
            height="48"
            viewBox="0 0 48 48"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M24 4L8 12v12c0 11.25 7.5 21.75 18 27 10.5-5.25 18-15.75 18-27V12L24 4z"
              fill="currentColor"
              opacity="0.2"
            />
            <path
              d="M24 4L8 12v12c0 11.25 7.5 21.75 18 27 10.5-5.25 18-15.75 18-27V12L24 4z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M18 24l4.5 4.5 9-9"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <h1 className="login-title">BWARM Dashboard</h1>
          <p className="login-subtitle">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && (
            <div className="login-error" role="alert">
              <svg
                className="error-icon"
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
              >
                <circle cx="10" cy="10" r="9" stroke="currentColor" strokeWidth="2" />
                <path
                  d="M10 6v5M10 14v1"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
              <span>{error}</span>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="form-input"
              required
              autoComplete="email"
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="form-input"
              required
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className="login-button"
            disabled={isLoading || !email || !password}
          >
            {isLoading ? (
              <>
                <svg
                  className="button-spinner"
                  width="20"
                  height="20"
                  viewBox="0 0 20 20"
                  fill="none"
                >
                  <circle
                    cx="10"
                    cy="10"
                    r="8"
                    stroke="currentColor"
                    strokeWidth="2"
                    opacity="0.25"
                  />
                  <path
                    d="M10 2a8 8 0 018 8"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
                Signing in...
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <div className="login-footer">
          <p className="demo-credentials">
            <strong>Demo Credentials:</strong>
            <br />
            Admin: admin@example.com / admin123
            <br />
            Publisher: publisher@example.com / publisher123
          </p>
        </div>
      </div>
    </div>
  );
};
