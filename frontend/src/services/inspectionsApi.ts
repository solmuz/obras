import apiClient from './api';
import {
  ExternalInspection,
  ExternalInspectionCreate,
  SiteInspection,
  SiteInspectionCreate,
  PaginationParams,
  InspectionStatus,
  InspectionCompany,
} from '@/types';

export const externalInspectionsApi = {
  list: async (
    params?: PaginationParams & { accessory_id?: string; company?: InspectionCompany; status?: InspectionStatus }
  ): Promise<ExternalInspection[]> => {
    const response = await apiClient.get<ExternalInspection[]>('/inspections/external', { params });
    return response.data;
  },

  get: async (inspectionId: string): Promise<ExternalInspection> => {
    const response = await apiClient.get<ExternalInspection>(`/inspections/external/${inspectionId}`);
    return response.data;
  },

  create: async (data: ExternalInspectionCreate): Promise<ExternalInspection> => {
    const response = await apiClient.post<ExternalInspection>('/inspections/external', data);
    return response.data;
  },

  update: async (inspectionId: string, data: Partial<ExternalInspectionCreate>): Promise<ExternalInspection> => {
    const response = await apiClient.patch<ExternalInspection>(`/inspections/external/${inspectionId}`, data);
    return response.data;
  },

  delete: async (inspectionId: string): Promise<void> => {
    await apiClient.delete(`/inspections/external/${inspectionId}`);
  },

  uploadCertificate: async (inspectionId: string, file: File): Promise<{ path: string }> => {
    const formData = new FormData();
    formData.append('certificate', file);
    const response = await apiClient.post(`/inspections/external/${inspectionId}/certificate`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};

export const siteInspectionsApi = {
  list: async (
    params?: PaginationParams & { accessory_id?: string; color_period?: string; status?: InspectionStatus }
  ): Promise<SiteInspection[]> => {
    const response = await apiClient.get<SiteInspection[]>('/inspections/site', { params });
    return response.data;
  },

  get: async (inspectionId: string): Promise<SiteInspection> => {
    const response = await apiClient.get<SiteInspection>(`/inspections/site/${inspectionId}`);
    return response.data;
  },

  create: async (data: SiteInspectionCreate): Promise<SiteInspection> => {
    const response = await apiClient.post<SiteInspection>('/inspections/site', data);
    return response.data;
  },

  update: async (inspectionId: string, data: Partial<SiteInspectionCreate>): Promise<SiteInspection> => {
    const response = await apiClient.patch<SiteInspection>(`/inspections/site/${inspectionId}`, data);
    return response.data;
  },

  delete: async (inspectionId: string): Promise<void> => {
    await apiClient.delete(`/inspections/site/${inspectionId}`);
  },

  uploadPhoto: async (inspectionId: string, file: File): Promise<{ path: string }> => {
    const formData = new FormData();
    formData.append('photo', file);
    const response = await apiClient.post(`/inspections/site/${inspectionId}/photos`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};
