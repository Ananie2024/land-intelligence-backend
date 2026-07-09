import { BaseEntity } from './common';

export type ProjectStatus = 'active' | 'planning' | 'completed' | 'suspended';

export interface Project extends BaseEntity {
  name: string;
  description?: string | null;
  parish_id?: string | null;
  status: ProjectStatus;
  budget?: number | null;
  start_date?: string | null;
  end_date?: string | null;
}

export interface ProjectCreate {
  name: string;
  description?: string | null;
  parish_id?: string | null;
  status: ProjectStatus;
  budget?: number | null;
  start_date?: string | null;
  end_date?: string | null;
}
