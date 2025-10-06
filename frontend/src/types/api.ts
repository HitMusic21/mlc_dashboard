/**
 * Common API types
 */

export interface Pagination {
  page: number;
  limit: number;
  total_items: number;
  total_pages: number;
}

export interface ResponseMeta {
  response_time_ms?: number;
  [key: string]: any;
}

export interface ErrorResponse {
  detail: string;
  status_code?: number;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RefreshRequest {
  refresh_token: string;
}

export interface UserResponse {
  id: number;
  email: string;
  full_name: string;
  role: 'publisher' | 'admin';
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export interface ApiRequestConfig {
  method?: HttpMethod;
  headers?: Record<string, string>;
  body?: any;
  params?: Record<string, any>;
}
