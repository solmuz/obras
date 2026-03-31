import axios, { AxiosInstance, AxiosError } from 'axios';
import { TokenResponse } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private instance: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.instance = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - add auth token
    this.instance.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor - handle token refresh
    this.instance.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalConfig = error.config;

        // If 401 and not a login request, try to refresh token
        if (error.response?.status === 401 && originalConfig?.url !== '/auth/login') {
          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await this.instance.post<TokenResponse>('/auth/refresh', {
                refresh_token: refreshToken,
              });

              const { access_token, refresh_token } = response.data;
              localStorage.setItem('access_token', access_token);
              localStorage.setItem('refresh_token', refresh_token);

              // Retry original request
              if (originalConfig?.headers) {
                originalConfig.headers.Authorization = `Bearer ${access_token}`;
              }
              return this.instance(originalConfig!);
            }
          } catch (refreshError) {
            // Refresh failed, clear tokens and redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  get client(): AxiosInstance {
    return this.instance;
  }

  setToken(token: string, refreshToken: string) {
    this.token = token;
    localStorage.setItem('access_token', token);
    localStorage.setItem('refresh_token', refreshToken);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}

export const apiClient = new ApiClient();
export default apiClient.client;
