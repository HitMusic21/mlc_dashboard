/**
 * MobileNav Component
 *
 * Mobile navigation menu with hamburger button.
 * Features:
 * - Hamburger menu animation
 * - Slide-in navigation drawer
 * - Touch-friendly tap targets
 * - Backdrop overlay
 * - Smooth animations
 */

import React, { useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import type { UserResponse } from '../../types/api';
import '../../styles/components/MobileNav.css';

interface MobileNavProps {
  isOpen: boolean;
  onToggle: () => void;
  user: UserResponse | null;
}

export const MobileNav: React.FC<MobileNavProps> = ({ isOpen, onToggle, user }) => {
  // Prevent body scroll when menu is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onToggle();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onToggle]);

  return (
    <>
      {/* Hamburger Button */}
      <button
        type="button"
        className={`mobile-nav-toggle ${isOpen ? 'open' : ''}`}
        onClick={onToggle}
        aria-label={isOpen ? 'Close menu' : 'Open menu'}
        aria-expanded={isOpen}
      >
        <span className="hamburger-line"></span>
        <span className="hamburger-line"></span>
        <span className="hamburger-line"></span>
      </button>

      {/* Backdrop */}
      {isOpen && (
        <div
          className="mobile-nav-backdrop"
          onClick={onToggle}
          aria-hidden="true"
        />
      )}

      {/* Navigation Drawer */}
      <nav
        className={`mobile-nav-drawer ${isOpen ? 'open' : ''}`}
        aria-label="Mobile navigation"
      >
        <div className="mobile-nav-header">
          <div className="mobile-nav-user">
            <div className="mobile-nav-avatar">
              {user?.full_name?.charAt(0).toUpperCase() || user?.email?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="mobile-nav-user-info">
              <div className="mobile-nav-user-name">{user?.full_name || user?.email}</div>
              <div className="mobile-nav-user-role">{user?.role}</div>
            </div>
          </div>
        </div>

        <div className="mobile-nav-links">
          <NavLink to="/" className="mobile-nav-link" onClick={onToggle} end>
            <svg viewBox="0 0 20 20" fill="currentColor" width="20" height="20">
              <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
            </svg>
            <span>Dashboard</span>
          </NavLink>

          <NavLink to="/works" className="mobile-nav-link" onClick={onToggle}>
            <svg viewBox="0 0 20 20" fill="currentColor" width="20" height="20">
              <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
            </svg>
            <span>Browse Works</span>
          </NavLink>

          <NavLink to="/catalog" className="mobile-nav-link" onClick={onToggle}>
            <svg viewBox="0 0 20 20" fill="currentColor" width="20" height="20">
              <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
            </svg>
            <span>Catalog Matcher</span>
          </NavLink>

          <NavLink to="/notifications" className="mobile-nav-link" onClick={onToggle}>
            <svg viewBox="0 0 20 20" fill="currentColor" width="20" height="20">
              <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
            </svg>
            <span>Notifications</span>
          </NavLink>

          {user?.role === 'admin' && (
            <NavLink to="/admin" className="mobile-nav-link" onClick={onToggle}>
              <svg viewBox="0 0 20 20" fill="currentColor" width="20" height="20">
                <path
                  fillRule="evenodd"
                  d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z"
                  clipRule="evenodd"
                />
              </svg>
              <span>Admin</span>
            </NavLink>
          )}
        </div>
      </nav>
    </>
  );
};
