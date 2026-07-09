import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { Project, ProjectCreate } from '@/types/project';
import { APIResponse } from '@/types/api';

/**
 * Project Service
 * 
 * Note: The backend currently does not have /projects endpoints implemented.
 * These methods are prepared for future backend implementation.
 * When the backend is ready, the endpoints will match ENDPOINTS.PROJECTS
 */
export const projectService = {
  getProjects: async (params?: { parish_id?: string; status?: string }): Promise<APIResponse<Project[]>> => {
    // TODO: Backend endpoint not yet implemented
    return apiClient.get<Project[]>(ENDPOINTS.PROJECTS.BASE, params);
  },

  getProjectById: async (id: string): Promise<APIResponse<Project>> => {
    // TODO: Backend endpoint not yet implemented
    return apiClient.get<Project>(ENDPOINTS.PROJECTS.BY_ID(id));
  },

  createProject: async (project: ProjectCreate): Promise<APIResponse<Project>> => {
    // TODO: Backend endpoint not yet implemented
    return apiClient.post<Project>(ENDPOINTS.PROJECTS.BASE, project);
  },

  updateProject: async (id: string, project: Partial<Project>): Promise<APIResponse<Project>> => {
    // TODO: Backend endpoint not yet implemented
    return apiClient.patch<Project>(ENDPOINTS.PROJECTS.BY_ID(id), project);
  },

  deleteProject: async (id: string): Promise<APIResponse<{ message: string }>> => {
    // TODO: Backend endpoint not yet implemented
    return apiClient.delete<{ message: string }>(ENDPOINTS.PROJECTS.BY_ID(id));
  },
};

export default projectService;