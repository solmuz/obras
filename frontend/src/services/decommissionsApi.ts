import apiClient from './api';
import { Decommission, DecommissionCreate, PaginationParams } from '@/types';

export const decommissionsApi = {
  list: async (params?: PaginationParams & { accessory_id?: string }): Promise<Decommission[]> => {
    const response = await apiClient.get<Decommission[]>('/decommissions', { params });
    return response.data;
  },

  get: async (decommissionId: string): Promise<Decommission> => {
    const response = await apiClient.get<Decommission>(`/decommissions/${decommissionId}`);
    return response.data;
  },

  create: async (data: DecommissionCreate): Promise<Decommission> => {
    const response = await apiClient.post<Decommission>('/decommissions', data);
    return response.data;
  },

  update: async (decommissionId: string, data: Partial<DecommissionCreate>): Promise<Decommission> => {
    const response = await apiClient.patch<Decommission>(`/decommissions/${decommissionId}`, data);
    return response.data;
  },

  delete: async (decommissionId: string): Promise<void> => {
    await apiClient.delete(`/decommissions/${decommissionId}`);
  },

  uploadPhoto: async (decommissionId: string, file: File): Promise<{ path: string }> => {
    const formData = new FormData();
    formData.append('photo', file);
    const response = await apiClient.post(`/decommissions/${decommissionId}/photos`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};
