/**
 * API client with authentication and error handling
 */

import axios, { type AxiosInstance, AxiosError } from 'axios';
import type {
  LoginRequest,
  TokenResponse,
  UserResponse,
} from '../types/api';
import type {
  WorksListResponse,
  WorkSearchRequest,
  WorkSearchResponse,
  DashboardStatisticsResponse,
  MLCStatisticsResponse,
  MusicalWorkDetailed,
} from '../types/works';
import type {
  CatalogUploadResponse,
  CatalogUploadsListResponse,
  CatalogUploadStatusResponse,
  CatalogResultsResponse,
} from '../types/catalog';
import type {
  UserPreferences,
  UserPreferencesUpdate,
  DashboardLayoutUpdate,
  SaveSearchRequest,
} from '../types/preferences';
import type {
  Notification,
  NotificationListResponse,
  UnreadCountResponse,
  MarkAllReadResponse,
} from '../types/notifications';
import type {
  SavedSearch,
  SavedSearchCreate,
  SavedSearchUpdate,
  SavedSearchListResponse,
} from '../types/savedSearch';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

class ApiClient {
  private client: AxiosInstance;
  private refreshPromise: Promise<string> | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}${API_PREFIX}`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor: Add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor: Handle 401 and refresh token
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any;

        // Handle 401 Unauthorized
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            // Attempt token refresh
            const newToken = await this.refreshAccessToken();
            if (newToken) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed - redirect to login
            this.clearTokens();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Token management
  private getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  private setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  private clearTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  private async refreshAccessToken(): Promise<string | null> {
    // Prevent multiple simultaneous refresh requests
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return null;
    }

    this.refreshPromise = (async () => {
      try {
        const response = await axios.post<TokenResponse>(
          `${API_BASE_URL}${API_PREFIX}/auth/refresh`,
          { refresh_token: refreshToken }
        );

        const { access_token, refresh_token: new_refresh_token } = response.data;
        this.setTokens(access_token, new_refresh_token);

        return access_token;
      } finally {
        this.refreshPromise = null;
      }
    })();

    return this.refreshPromise;
  }

  // Authentication endpoints
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>('/auth/login', credentials);
    this.setTokens(response.data.access_token, response.data.refresh_token);
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/auth/logout');
    } finally {
      this.clearTokens();
    }
  }

  async getCurrentUser(): Promise<UserResponse> {
    const response = await this.client.get<UserResponse>('/auth/me');
    return response.data;
  }

  // Works endpoints
  async getWorks(params?: {
    page?: number;
    limit?: number;
    search?: string;
    has_iswc?: boolean;
    has_disputed_rights?: boolean;
    created_after?: string;
    created_before?: string;
  }): Promise<WorksListResponse> {
    const response = await this.client.get<WorksListResponse>('/works', { params });
    return response.data;
  }

  async getWork(id: number): Promise<MusicalWorkDetailed> {
    const response = await this.client.get<MusicalWorkDetailed>(`/works/${id}`);
    return response.data;
  }

  async searchWorks(request: WorkSearchRequest): Promise<WorkSearchResponse> {
    const response = await this.client.post<WorkSearchResponse>('/works/search', request);
    return response.data;
  }

  async getStatistics(): Promise<DashboardStatisticsResponse> {
    const response = await this.client.get<DashboardStatisticsResponse>('/works/statistics');
    return response.data;
  }

  async getMLCStatistics(): Promise<MLCStatisticsResponse> {
    const response = await this.client.get<MLCStatisticsResponse>('/works/statistics/mlc');
    return response.data;
  }

  // Catalog endpoints
  async uploadCatalog(
    file: File,
    publisherName: string
  ): Promise<CatalogUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('publisher_name', publisherName);

    const response = await this.client.post<CatalogUploadResponse>(
      '/catalog/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  async getCatalogUploads(params?: {
    page?: number;
    limit?: number;
    status?: string;
  }): Promise<CatalogUploadsListResponse> {
    const response = await this.client.get<CatalogUploadsListResponse>(
      '/catalog/uploads',
      { params }
    );
    return response.data;
  }

  async getUploadStatus(uploadId: number): Promise<CatalogUploadStatusResponse> {
    const response = await this.client.get<CatalogUploadStatusResponse>(
      `/catalog/${uploadId}/status`
    );
    return response.data;
  }

  async getUploadResults(
    uploadId: number,
    params?: {
      page?: number;
      limit?: number;
      confidence?: string;
      min_score?: number;
    }
  ): Promise<CatalogResultsResponse> {
    const response = await this.client.get<CatalogResultsResponse>(
      `/catalog/${uploadId}/results`,
      { params }
    );
    return response.data;
  }

  async exportUploadResults(
    uploadId: number,
    format: 'csv' | 'excel',
    params?: {
      confidence?: string;
    }
  ): Promise<Blob> {
    const response = await this.client.get(`/catalog/${uploadId}/export`, {
      params: { ...params, format },
      responseType: 'blob',
    });
    return response.data;
  }

  async deleteUpload(uploadId: number): Promise<void> {
    await this.client.delete(`/catalog/${uploadId}`);
  }

  // Admin endpoints
  async getAllUploads(params?: {
    page?: number;
    limit?: number;
    status?: string;
    user_id?: number;
  }): Promise<CatalogUploadsListResponse> {
    const response = await this.client.get<CatalogUploadsListResponse>(
      '/admin/uploads',
      { params }
    );
    return response.data;
  }

  async getUsers(params?: {
    page?: number;
    limit?: number;
    role?: string;
    is_active?: boolean;
  }): Promise<any> {
    const response = await this.client.get('/admin/users', { params });
    return response.data;
  }

  async getAllUsers(params?: {
    page?: number;
    limit?: number;
    role?: string;
    is_active?: boolean;
  }): Promise<any> {
    const response = await this.client.get('/admin/users', { params });
    return response.data;
  }

  async getAdminStatistics(): Promise<any> {
    const response = await this.client.get('/admin/statistics');
    return response.data;
  }

  // User Preferences endpoints
  async getPreferences(): Promise<UserPreferences> {
    const response = await this.client.get<UserPreferences>('/preferences');
    return response.data;
  }

  async updatePreferences(updates: UserPreferencesUpdate): Promise<UserPreferences> {
    const response = await this.client.put<UserPreferences>('/preferences', updates);
    return response.data;
  }

  async updateDashboardLayout(layout: DashboardLayoutUpdate): Promise<UserPreferences> {
    const response = await this.client.post<UserPreferences>('/preferences/layout', layout);
    return response.data;
  }

  async saveSearch(search: SaveSearchRequest): Promise<UserPreferences> {
    const response = await this.client.post<UserPreferences>('/preferences/searches', search);
    return response.data;
  }

  async deleteSavedSearch(searchId: string): Promise<UserPreferences> {
    const response = await this.client.delete<UserPreferences>(`/preferences/searches/${searchId}`);
    return response.data;
  }

  // Notifications endpoints
  async getNotifications(params?: {
    is_read?: boolean;
    page?: number;
    limit?: number;
  }): Promise<NotificationListResponse> {
    const response = await this.client.get<NotificationListResponse>('/notifications', { params });
    return response.data;
  }

  async getUnreadCount(): Promise<UnreadCountResponse> {
    const response = await this.client.get<UnreadCountResponse>('/notifications/unread-count');
    return response.data;
  }

  async markNotificationAsRead(notificationId: string): Promise<Notification> {
    const response = await this.client.put<Notification>(`/notifications/${notificationId}/read`);
    return response.data;
  }

  async markAllNotificationsAsRead(): Promise<MarkAllReadResponse> {
    const response = await this.client.put<MarkAllReadResponse>('/notifications/read-all');
    return response.data;
  }

  async deleteNotification(notificationId: string): Promise<void> {
    await this.client.delete(`/notifications/${notificationId}`);
  }

  async clearReadNotifications(): Promise<{ deleted_count: number }> {
    const response = await this.client.delete<{ deleted_count: number }>('/notifications/clear-read');
    return response.data;
  }

  // ==================== Saved Searches ====================

  async getSavedSearches(params?: {
    include_presets?: boolean;
    favorites_only?: boolean;
  }): Promise<SavedSearchListResponse> {
    const response = await this.client.get<SavedSearchListResponse>('/saved-searches', { params });
    return response.data;
  }

  async getSavedSearch(searchId: number): Promise<SavedSearch> {
    const response = await this.client.get<SavedSearch>(`/saved-searches/${searchId}`);
    return response.data;
  }

  async getSystemPresets(): Promise<SavedSearch[]> {
    const response = await this.client.get<SavedSearch[]>('/saved-searches/presets');
    return response.data;
  }

  async createSavedSearch(search: SavedSearchCreate): Promise<SavedSearch> {
    const response = await this.client.post<SavedSearch>('/saved-searches', search);
    return response.data;
  }

  async updateSavedSearch(searchId: number, updates: SavedSearchUpdate): Promise<SavedSearch> {
    const response = await this.client.put<SavedSearch>(`/saved-searches/${searchId}`, updates);
    return response.data;
  }

  async deleteSavedSearchNew(searchId: number): Promise<void> {
    await this.client.delete(`/saved-searches/${searchId}`);
  }

  async recordSearchUse(searchId: number): Promise<SavedSearch> {
    const response = await this.client.post<SavedSearch>(`/saved-searches/${searchId}/use`);
    return response.data;
  }

  async bulkDeleteSearches(searchIds: number[]): Promise<{ deleted_count: number; total_requested: number }> {
    const response = await this.client.post<{ deleted_count: number; total_requested: number }>(
      '/saved-searches/bulk-delete',
      searchIds
    );
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
