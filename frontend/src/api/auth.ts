import { apiClient } from './axios';
import type { LoginRequest, LoginResponse, User } from '../types';

export interface RegisterRequest {
  username: string;
  email: string;
  mot_de_passe: string;
  role?: string;
}

export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post('/auth/login', {
      email: credentials.username.trim().toLowerCase(),
      mot_de_passe: credentials.password,
    });
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<User> => {
    const response = await apiClient.post('/auth/register', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
  },
};
