import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';

import { useAuthStore } from '../store/auth';
import { useUiStore } from '../store/ui';
import { translate } from '../i18n';

export class ApiError extends Error {
  status?: number;

  detail: string;

  constructor(detail: string, status?: number) {
    super(detail);
    this.name = 'ApiError';
    this.detail = detail;
    this.status = status;
  }
}

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

const AUTH_PATH_PREFIX = '/api/auth/';

function createClient() {
  return axios.create({
    baseURL: import.meta.env.VITE_BACKEND_HTTP_URL || '',
    timeout: 20000,
    withCredentials: true,
  });
}

export const baseHttp = createClient();
export const http = createClient();

let refreshPromise: Promise<void> | null = null;

function shouldSkipRefresh(url?: string): boolean {
  if (!url) {
    return false;
  }
  return url === '/api/health' || url === '/api/auth/refresh' || url.startsWith(`${AUTH_PATH_PREFIX}login`);
}

function handleUnauthorized(detail: string) {
  useAuthStore.getState().markUnauthenticated(detail || translate('http.sessionInvalid'));
  if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
    window.location.assign('/login');
  }
}

async function refreshOnce(): Promise<void> {
  if (!refreshPromise) {
    refreshPromise = baseHttp
      .post('/api/auth/refresh')
      .then(() => {
        useAuthStore.getState().clearAuthNotice();
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

http.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<{ detail?: string }>) => {
    const detail = error.response?.data?.detail || error.message || translate('http.requestFailed');
    const apiError = new ApiError(detail, error.response?.status);
    const originalRequest = error.config as RetryableRequestConfig | undefined;

    if (apiError.status === 401 && originalRequest && !originalRequest._retry && !shouldSkipRefresh(originalRequest.url)) {
      originalRequest._retry = true;
      try {
        await refreshOnce();
        return await http(originalRequest);
      } catch {
        handleUnauthorized(translate('http.sessionExpired'));
        return Promise.reject(new ApiError(translate('http.sessionExpired'), 401));
      }
    }

    if (apiError.status === 401) {
      handleUnauthorized(detail);
    }
    if (apiError.status === 503) {
      useUiStore.getState().pushToast({
        tone: 'warning',
        title: translate('http.backendNotReadyTitle'),
        message: translate('http.backendNotReadyMessage'),
      });
    }

    return Promise.reject(apiError);
  },
);

export function getErrorMessage(error: unknown, fallback = translate('http.requestFailed')): string {
  if (error instanceof ApiError) {
    return error.detail;
  }
  if (axios.isAxiosError<{ detail?: string }>(error)) {
    const detail = error.response?.data?.detail;
    if (detail) {
      return detail;
    }
  }
  if (error instanceof Error) {
    return error.message;
  }
  return fallback;
}
