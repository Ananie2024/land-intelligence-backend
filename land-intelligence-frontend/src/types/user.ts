import { BaseEntity } from './common';

export type UserRole = 'admin' | 'client' | 'viewer';

export interface UserBase {
  email: string;
  username: string;
  full_name?: string | null;
}

export interface UserCreate extends UserBase {
  password?: string;
  role: UserRole;
  parish_id?: string | null;
}

export interface UserResponse extends UserBase, BaseEntity {
  role: UserRole;
  parish_id?: string | null;
  is_active: boolean;
  is_verified: boolean;
  last_login?: string | null;
}

export interface UserLogin {
  username: string;
  password?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: UserResponse;
}

export interface UserListResponse {
  items: UserResponse[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface PasswordChange {
  current_password?: string;
  new_password?: string;
}
