import apiClient from './api';
import { User, UserCreate, UserUpdate, PaginationParams } from '@/types';

export const usersApi = {
  listUsers: async (params?: PaginationParams & { role?: string; is_active?: boolean }): Promise<User[]> => {
    const response = await apiClient.get<User[]>('/users', { params });
    return response.data;
  },

  getUser: async (userId: string): Promise<User> => {
    const response = await apiClient.get<User>(`/users/${userId}`);
    return response.data;
  },

  createUser: async (userData: UserCreate): Promise<User> => {
    const response = await apiClient.post<User>('/users', userData);
    return response.data;
  },

  updateUser: async (userId: string, userData: UserUpdate): Promise<User> => {
    const response = await apiClient.patch<User>(`/users/${userId}`, userData);
    return response.data;
  },

  deleteUser: async (userId: string): Promise<void> => {
    await apiClient.delete(`/users/${userId}`);
  },
};
