import apiClient from './api';
import { AccessoryListItem, PaginationParams, AccessoryStatus, ElementType, Brand } from '@/types';

export const reportsApi = {
  getSemaforo: async (
    params?: PaginationParams & {
      semaforo_status?: string;
      project_id?: string;
      element_type?: ElementType;
      brand?: Brand;
      usage_status?: AccessoryStatus;
    }
  ): Promise<AccessoryListItem[]> => {
    const response = await apiClient.get<AccessoryListItem[]>('/reports/semaforo', { params });
    return response.data;
  },

  getProjectSemaforo: async (projectId: string): Promise<{
    verde_count: number;
    amarillo_count: number;
    rojo_count: number;
    verde: AccessoryListItem[];
    amarillo: AccessoryListItem[];
    rojo: AccessoryListItem[];
  }> => {
    const response = await apiClient.get(`/reports/semaforo/by-project/${projectId}`);
    return response.data;
  },

  exportPdf: async (params?: { semaforo_status?: string; project_id?: string }): Promise<Blob> => {
    const response = await apiClient.post('/reports/export-pdf', null, {
      params,
      responseType: 'blob',
    });
    return response.data;
  },
};
