/**
 * User Preferences Store
 *
 * Zustand store for managing user preferences state.
 * Handles theme, dashboard layout, saved searches, and pagination settings.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiClient } from '../services/api';
import type {
  UserPreferences,
  UserPreferencesUpdate,
  DashboardLayoutConfig,
  ThemePreference,
} from '../types/preferences';

interface PreferencesState {
  // State
  preferences: UserPreferences | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchPreferences: () => Promise<void>;
  updatePreferences: (updates: UserPreferencesUpdate) => Promise<void>;
  updateDashboardLayout: (layout: DashboardLayoutConfig) => Promise<void>;
  saveSearch: (name: string, filters: Record<string, unknown>) => Promise<void>;
  deleteSavedSearch: (searchId: string) => Promise<void>;
  setTheme: (theme: ThemePreference) => Promise<void>;
  setItemsPerPage: (itemsPerPage: number) => Promise<void>;
  reset: () => void;
}

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set) => ({
      // Initial state
      preferences: null,
      isLoading: false,
      error: null,

      // Fetch user preferences
      fetchPreferences: async () => {
        set({ isLoading: true, error: null });
        try {
          const preferences = await apiClient.getPreferences();
          set({ preferences, isLoading: false });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to fetch preferences';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      // Update preferences
      updatePreferences: async (updates: UserPreferencesUpdate) => {
        set({ isLoading: true, error: null });
        try {
          const preferences = await apiClient.updatePreferences(updates);
          set({ preferences, isLoading: false });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to update preferences';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      // Update dashboard layout
      updateDashboardLayout: async (layout: DashboardLayoutConfig) => {
        set({ isLoading: true, error: null });
        try {
          const preferences = await apiClient.updateDashboardLayout({ layout });
          set({ preferences, isLoading: false });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to update layout';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      // Save search
      saveSearch: async (name: string, filters: Record<string, unknown>) => {
        set({ isLoading: true, error: null });
        try {
          const preferences = await apiClient.saveSearch({ name, filters });
          set({ preferences, isLoading: false });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to save search';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      // Delete saved search
      deleteSavedSearch: async (searchId: string) => {
        set({ isLoading: true, error: null });
        try {
          const preferences = await apiClient.deleteSavedSearch(searchId);
          set({ preferences, isLoading: false });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to delete search';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      // Set theme preference
      setTheme: async (theme: ThemePreference) => {
        set({ isLoading: true, error: null });
        try {
          const preferences = await apiClient.updatePreferences({ theme });
          set({ preferences, isLoading: false });

          // Apply theme to document
          document.documentElement.setAttribute('data-theme', theme);
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to set theme';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      // Set items per page
      setItemsPerPage: async (itemsPerPage: number) => {
        set({ isLoading: true, error: null });
        try {
          const preferences = await apiClient.updatePreferences({ items_per_page: itemsPerPage });
          set({ preferences, isLoading: false });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to set items per page';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      // Reset state
      reset: () => {
        set({ preferences: null, isLoading: false, error: null });
      },
    }),
    {
      name: 'user-preferences-storage',
      partialize: (state) => ({
        // Only persist preferences data, not loading/error states
        preferences: state.preferences,
      }),
    }
  )
);

// Selectors for commonly used values
export const selectTheme = (state: PreferencesState) => state.preferences?.theme || 'auto';
export const selectItemsPerPage = (state: PreferencesState) => state.preferences?.items_per_page || 50;
export const selectDashboardLayout = (state: PreferencesState) => state.preferences?.dashboard_layout;
export const selectSavedSearches = (state: PreferencesState) => state.preferences?.saved_searches || [];
