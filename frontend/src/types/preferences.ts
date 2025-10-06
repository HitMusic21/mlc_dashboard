/**
 * User Preferences Types
 *
 * Type definitions for user preferences, dashboard layouts, and saved searches.
 */

export type ThemePreference = 'light' | 'dark' | 'auto';

export interface DashboardWidget {
  id: string;
  type: 'stat' | 'chart' | 'activity' | 'notifications' | 'searches';
  position: {
    x: number;
    y: number;
    w: number;
    h: number;
  };
}

export interface DashboardLayoutConfig {
  columns: number;
  widgets: DashboardWidget[];
}

export interface SavedSearchFilter {
  name: string;
  filters: Record<string, unknown>;
}

export interface UserPreferences {
  id: string;
  user_id: number;
  dashboard_layout: DashboardLayoutConfig | null;
  saved_searches: SavedSearchFilter[] | null;
  theme: ThemePreference;
  items_per_page: number;
  created_at: string;
  updated_at: string;
}

export interface UserPreferencesUpdate {
  dashboard_layout?: DashboardLayoutConfig;
  saved_searches?: SavedSearchFilter[];
  theme?: ThemePreference;
  items_per_page?: number;
}

export interface DashboardLayoutUpdate {
  layout: DashboardLayoutConfig;
}

export interface SaveSearchRequest {
  name: string;
  filters: Record<string, unknown>;
}
