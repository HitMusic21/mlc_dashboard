/**
 * PreferencesModal Component
 *
 * Modal dialog for managing user preferences.
 * Features:
 * - Theme selection (light, dark, auto)
 * - Items per page configuration
 * - Dashboard layout reset option
 * - Save and cancel actions
 */

import React, { useState, useEffect } from 'react';
import { usePreferencesStore } from '../../stores/usePreferencesStore';
import type { ThemePreference } from '../../types/preferences';
import '../../styles/components/PreferencesModal.css';

interface PreferencesModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const PreferencesModal: React.FC<PreferencesModalProps> = ({ isOpen, onClose }) => {
  const { preferences, updatePreferences, isLoading } = usePreferencesStore();

  const [theme, setTheme] = useState<ThemePreference>('auto');
  const [itemsPerPage, setItemsPerPage] = useState<number>(50);
  const [hasChanges, setHasChanges] = useState(false);

  // Initialize form values from preferences
  useEffect(() => {
    if (preferences) {
      setTheme(preferences.theme);
      setItemsPerPage(preferences.items_per_page);
    }
  }, [preferences]);

  // Track changes
  useEffect(() => {
    if (preferences) {
      const changed =
        theme !== preferences.theme || itemsPerPage !== preferences.items_per_page;
      setHasChanges(changed);
    }
  }, [theme, itemsPerPage, preferences]);

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose]);

  const handleSave = async () => {
    try {
      await updatePreferences({
        theme,
        items_per_page: itemsPerPage,
      });
      onClose();
    } catch (error) {
      console.error('Failed to save preferences:', error);
    }
  };

  const handleCancel = () => {
    // Reset to current preferences
    if (preferences) {
      setTheme(preferences.theme);
      setItemsPerPage(preferences.items_per_page);
    }
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={handleCancel}>
      <div className="preferences-modal modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <h2 className="modal-title">Preferences</h2>
          <button
            type="button"
            className="btn btn-ghost btn-sm preferences-modal__close"
            onClick={handleCancel}
            aria-label="Close"
          >
            <svg viewBox="0 0 20 20" fill="currentColor" width="20" height="20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="modal-body">
          {/* Theme Selection */}
          <div className="preferences-modal__section">
            <label className="preferences-modal__label">
              <span className="preferences-modal__label-text">Theme</span>
              <span className="preferences-modal__label-description">
                Choose your preferred color scheme
              </span>
            </label>

            <div className="preferences-modal__theme-options">
              <button
                type="button"
                className={`preferences-modal__theme-option ${
                  theme === 'light' ? 'preferences-modal__theme-option--active' : ''
                }`}
                onClick={() => setTheme('light')}
              >
                <svg viewBox="0 0 20 20" fill="currentColor" width="24" height="24">
                  <path
                    fillRule="evenodd"
                    d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>Light</span>
              </button>

              <button
                type="button"
                className={`preferences-modal__theme-option ${
                  theme === 'dark' ? 'preferences-modal__theme-option--active' : ''
                }`}
                onClick={() => setTheme('dark')}
              >
                <svg viewBox="0 0 20 20" fill="currentColor" width="24" height="24">
                  <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                </svg>
                <span>Dark</span>
              </button>

              <button
                type="button"
                className={`preferences-modal__theme-option ${
                  theme === 'auto' ? 'preferences-modal__theme-option--active' : ''
                }`}
                onClick={() => setTheme('auto')}
              >
                <svg viewBox="0 0 20 20" fill="currentColor" width="24" height="24">
                  <path
                    fillRule="evenodd"
                    d="M3 5a2 2 0 012-2h10a2 2 0 012 2v8a2 2 0 01-2 2h-2.22l.123.489.804.804A1 1 0 0113 18H7a1 1 0 01-.707-1.707l.804-.804L7.22 15H5a2 2 0 01-2-2V5zm5.771 7H5V5h10v7H8.771z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>Auto</span>
              </button>
            </div>
          </div>

          <div className="divider" />

          {/* Items Per Page */}
          <div className="preferences-modal__section">
            <label className="preferences-modal__label">
              <span className="preferences-modal__label-text">Items per page</span>
              <span className="preferences-modal__label-description">
                Number of items to display in tables
              </span>
            </label>

            <select
              className="select preferences-modal__select"
              value={itemsPerPage}
              onChange={(e) => setItemsPerPage(Number(e.target.value))}
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value={200}>200</option>
            </select>
          </div>
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button type="button" className="btn btn-secondary" onClick={handleCancel}>
            Cancel
          </button>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleSave}
            disabled={!hasChanges || isLoading}
          >
            {isLoading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PreferencesModal;
