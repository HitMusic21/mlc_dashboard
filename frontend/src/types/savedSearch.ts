/**
 * Saved Search Type Definitions
 */

export type FilterOperator =
  | "equals"
  | "not_equals"
  | "contains"
  | "not_contains"
  | "starts_with"
  | "ends_with"
  | "greater_than"
  | "less_than"
  | "greater_than_or_equal"
  | "less_than_or_equal"
  | "in"
  | "not_in"
  | "is_null"
  | "is_not_null";

export interface FilterCondition {
  field: string;
  operator: FilterOperator;
  value: any;
}

export interface FilterConfig {
  logic: "AND" | "OR";
  filters: FilterCondition[];
  sort?: {
    field: string;
    order: "asc" | "desc";
  };
}

export interface SavedSearch {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  filter_config: FilterConfig;
  is_preset: boolean;
  is_favorite: boolean;
  last_used_at?: string;
  use_count: number;
  created_at: string;
  updated_at: string;
}

export interface SavedSearchCreate {
  name: string;
  description?: string;
  filter_config: FilterConfig;
  is_favorite?: boolean;
}

export interface SavedSearchUpdate {
  name?: string;
  description?: string;
  filter_config?: FilterConfig;
  is_favorite?: boolean;
}

export interface SavedSearchListResponse {
  total: number;
  searches: SavedSearch[];
}
