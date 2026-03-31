import apiClient from './api';
import { Project, ProjectDetail, ProjectCreate, ProjectUpdate, PaginationParams, ProjectStatus } from '@/types';

export const projectsApi = {
  listProjects: async (params?: PaginationParams & { status?: ProjectStatus }): Promise<Project[]> => {
    const response = await apiClient.get<Project[]>('/projects', { params });
    return response.data;
  },

  getProject: async (projectId: string): Promise<ProjectDetail> => {
    const response = await apiClient.get<ProjectDetail>(`/projects/${projectId}`);
    return response.data;
  },

  createProject: async (projectData: ProjectCreate): Promise<Project> => {
    const response = await apiClient.post<Project>('/projects', projectData);
    return response.data;
  },

  updateProject: async (projectId: string, projectData: ProjectUpdate): Promise<Project> => {
    const response = await apiClient.patch<Project>(`/projects/${projectId}`, projectData);
    return response.data;
  },

  deleteProject: async (projectId: string): Promise<void> => {
    await apiClient.delete(`/projects/${projectId}`);
  },

  assignEmployee: async (projectId: string, userId: string): Promise<ProjectDetail> => {
    const response = await apiClient.post<ProjectDetail>(`/projects/${projectId}/assign-employee`, {
      user_id: userId,
    });
    return response.data;
  },

  removeEmployee: async (projectId: string, userId: string): Promise<void> => {
    await apiClient.delete(`/projects/${projectId}/employees/${userId}`);
  },
};
