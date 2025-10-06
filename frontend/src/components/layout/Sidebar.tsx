import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';

interface SidebarProps {
  isOpen?: boolean;
  onToggle?: () => void;
  userRole?: 'publisher' | 'admin';
  className?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen = true,
  onToggle,
  userRole,
  className = '',
}) => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  const navItems = [
    {
      path: '/',
      label: 'Dashboard',
      icon: (
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path
            d="M3 9l7-7 7 7v8a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      ),
    },
    {
      path: '/works',
      label: 'Browse Works',
      icon: (
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path
            d="M9 17A8 8 0 119 1a8 8 0 010 16zM19 19l-4.35-4.35"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      ),
    },
    {
      path: '/catalog',
      label: 'Catalog Matcher',
      icon: (
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path
            d="M14 2H6a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V4a2 2 0 00-2-2zM8 10h4M8 14h2"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      ),
    },
  ];

  // Add admin-only items
  if (userRole === 'admin') {
    navItems.push({
      path: '/admin',
      label: 'Admin Panel',
      icon: (
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path
            d="M12 14a4 4 0 100-8 4 4 0 000 8zM19 19l-2.5-2.5"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="6" cy="6" r="3" stroke="currentColor" strokeWidth="2" />
        </svg>
      ),
    });
  }

  return (
    <aside className={`sidebar ${isOpen ? 'open' : 'closed'} ${className}`}>
      {/* Mobile toggle button */}
      {onToggle && (
        <button
          type="button"
          className="sidebar-toggle mobile-only"
          onClick={onToggle}
          aria-label={isOpen ? 'Close sidebar' : 'Open sidebar'}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            {isOpen ? (
              <path
                d="M18 6L6 18M6 6l12 12"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            ) : (
              <path
                d="M3 12h18M3 6h18M3 18h18"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            )}
          </svg>
        </button>
      )}

      {/* Navigation */}
      <nav className="sidebar-nav" aria-label="Sidebar navigation">
        <ul className="nav-list">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                aria-current={isActive(item.path) ? 'page' : undefined}
                end={item.path === '/'}
              >
                <span className="nav-icon" aria-hidden="true">
                  {item.icon}
                </span>
                <span className="nav-label">{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Collapse button (desktop only) */}
      {onToggle && (
        <button
          type="button"
          className="sidebar-collapse desktop-only"
          onClick={onToggle}
          aria-label={isOpen ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            className={isOpen ? '' : 'rotate-180'}
          >
            <path
              d="M10 4L6 8l4 4"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      )}
    </aside>
  );
};
