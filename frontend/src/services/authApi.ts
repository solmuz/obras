import apiClient from './api';
import { LoginRequest, TokenResponse, User } from '@/types';

export const authApi = {
  login: async (credentials: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/login', credentials);
    return response.data;
  },

  refresh: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },

  getProfile: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/profile');
    return response.data;
  },
};
