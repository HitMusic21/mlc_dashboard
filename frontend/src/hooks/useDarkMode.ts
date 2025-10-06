/**
 * useDarkMode Hook
 *
 * Manages theme state with localStorage persistence and API synchronization.
 * Supports light, dark, and auto (system preference) themes.
 */

import { useEffect, useState } from 'react';

export type Theme = 'light' | 'dark' | 'auto';

interface UseDarkModeReturn {
  theme: Theme;
  isDarkMode: boolean;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

const STORAGE_KEY = 'theme-preference';
const DEFAULT_THEME: Theme = 'auto';

/**
 * Gets the system color scheme preference
 */
const getSystemPreference = (): 'light' | 'dark' => {
  if (typeof window === 'undefined') return 'light';

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

/**
 * Resolves the effective theme based on current theme setting
 */
const resolveTheme = (theme: Theme): 'light' | 'dark' => {
  if (theme === 'auto') {
    return getSystemPreference();
  }
  return theme;
};

/**
 * Applies theme to document
 */
const applyTheme = (theme: 'light' | 'dark') => {
  if (typeof document === 'undefined') return;

  document.documentElement.setAttribute('data-theme', theme);

  // Also update meta theme-color for mobile browsers
  const metaThemeColor = document.querySelector('meta[name="theme-color"]');
  if (metaThemeColor) {
    metaThemeColor.setAttribute(
      'content',
      theme === 'dark' ? '#111827' : '#ffffff'
    );
  }
};

/**
 * Saves theme preference to localStorage
 */
const saveToStorage = (theme: Theme) => {
  try {
    localStorage.setItem(STORAGE_KEY, theme);
  } catch (error) {
    console.warn('Failed to save theme preference to localStorage:', error);
  }
};

/**
 * Loads theme preference from localStorage
 */
const loadFromStorage = (): Theme => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'light' || stored === 'dark' || stored === 'auto') {
      return stored;
    }
  } catch (error) {
    console.warn('Failed to load theme preference from localStorage:', error);
  }
  return DEFAULT_THEME;
};

/**
 * Syncs theme preference with backend API
 */
const syncWithAPI = async (theme: Theme) => {
  try {
    const response = await fetch('/api/v1/preferences', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        // Authorization header will be added by auth interceptor
      },
      body: JSON.stringify({ theme }),
    });

    if (!response.ok) {
      console.warn('Failed to sync theme with API:', response.statusText);
    }
  } catch (error) {
    console.warn('Failed to sync theme with API:', error);
    // Don't throw - this is a non-critical operation
  }
};

/**
 * Custom hook for managing dark mode with localStorage and API sync
 */
export const useDarkMode = (): UseDarkModeReturn => {
  const [theme, setThemeState] = useState<Theme>(() => loadFromStorage());
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    const initialTheme = loadFromStorage();
    return resolveTheme(initialTheme) === 'dark';
  });

  // Apply theme on mount and when theme changes
  useEffect(() => {
    const effectiveTheme = resolveTheme(theme);
    applyTheme(effectiveTheme);
    setIsDarkMode(effectiveTheme === 'dark');
  }, [theme]);

  // Listen for system preference changes when in auto mode
  useEffect(() => {
    if (theme !== 'auto') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = (e: MediaQueryListEvent) => {
      const effectiveTheme = e.matches ? 'dark' : 'light';
      applyTheme(effectiveTheme);
      setIsDarkMode(effectiveTheme === 'dark');
    };

    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
    // Legacy browsers
    else if (mediaQuery.addListener) {
      mediaQuery.addListener(handleChange);
      return () => mediaQuery.removeListener(handleChange);
    }
  }, [theme]);

  /**
   * Sets the theme and persists to localStorage and API
   */
  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    saveToStorage(newTheme);

    // Sync with API asynchronously (fire and forget)
    syncWithAPI(newTheme).catch(() => {
      // Error already logged in syncWithAPI
    });
  };

  /**
   * Toggles between light and dark themes
   * If currently in auto mode, switches to the opposite of system preference
   */
  const toggleTheme = () => {
    const currentEffective = resolveTheme(theme);
    const newTheme = currentEffective === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
  };

  return {
    theme,
    isDarkMode,
    setTheme,
    toggleTheme,
  };
};

/**
 * Hook for components that only need to know if dark mode is active
 * (without the ability to change it)
 */
export const useIsDarkMode = (): boolean => {
  const { isDarkMode } = useDarkMode();
  return isDarkMode;
};
