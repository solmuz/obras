import apiClient from './api';
import { Accessory, AccessoryCreate, AccessoryUpdate, AccessoryListItem, PaginationParams, AccessoryStatus, ElementType, Brand } from '@/types';

export const accessoriesApi = {
  listAccessories: async (
    params?: PaginationParams & { project_id?: string; status?: AccessoryStatus; element_type?: ElementType; brand?: Brand }
  ): Promise<AccessoryListItem[]> => {
    const response = await apiClient.get<AccessoryListItem[]>('/accessories', { params });
    return response.data;
  },

  getAccessory: async (accessoryId: string): Promise<Accessory> => {
    const response = await apiClient.get<Accessory>(`/accessories/${accessoryId}`);
    return response.data;
  },

  createAccessory: async (accessoryData: AccessoryCreate): Promise<Accessory> => {
    const response = await apiClient.post<Accessory>('/accessories', accessoryData);
    return response.data;
  },

  updateAccessory: async (accessoryId: string, accessoryData: AccessoryUpdate): Promise<Accessory> => {
    const response = await apiClient.patch<Accessory>(`/accessories/${accessoryId}`, accessoryData);
    return response.data;
  },

  deleteAccessory: async (accessoryId: string): Promise<void> => {
    await apiClient.delete(`/accessories/${accessoryId}`);
  },

  uploadPhoto: async (
    accessoryId: string,
    file: File,
    photoType: 'accessory' | 'manufacturer_label' | 'provider_marking'
  ): Promise<{ path: string }> => {
    const formData = new FormData();
    formData.append('photo', file);
    const response = await apiClient.post(`/accessories/${accessoryId}/photos`, formData, {
      params: { photo_type: photoType },
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};
