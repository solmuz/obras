import apiClient from './api';
import { AuditLog, PaginationParams } from '@/types';

export const auditApi = {
  list: async (
    params?: PaginationParams & { entity_type?: string; action?: string; user_id?: string }
  ): Promise<AuditLog[]> => {
    const response = await apiClient.get<AuditLog[]>('/audit-logs', { params });
    return response.data;
  },

  get: async (logId: string): Promise<AuditLog> => {
    const response = await apiClient.get<AuditLog>(`/audit-logs/${logId}`);
    return response.data;
  },
};
