import type { AuthLoginRequest, AuthSessionResponse, AuthUserResponse, HealthResponse } from './types';
import { baseHttp } from './http';

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await baseHttp.get<HealthResponse>('/api/health');
  return data;
}

export async function getCurrentUser(): Promise<AuthUserResponse> {
  const { data } = await baseHttp.get<AuthUserResponse>('/api/auth/me');
  return data;
}

export async function login(payload: AuthLoginRequest): Promise<AuthUserResponse> {
  const { data } = await baseHttp.post<AuthUserResponse>('/api/auth/login', payload);
  return data;
}

export async function refreshSession(): Promise<AuthUserResponse> {
  const { data } = await baseHttp.post<AuthUserResponse>('/api/auth/refresh');
  return data;
}

export async function logout(): Promise<void> {
  await baseHttp.post('/api/auth/logout');
}

export async function getAuthSession(): Promise<AuthSessionResponse> {
  const { data } = await baseHttp.get<AuthSessionResponse>('/api/auth/session');
  return data;
}
