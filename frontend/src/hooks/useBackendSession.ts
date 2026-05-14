import { useEffect } from 'react';
import axios from 'axios';
import { useQuery } from '@tanstack/react-query';

import { getCurrentUser, getHealth } from '../api/auth';
import { ApiError, getErrorMessage } from '../api/http';
import { translate } from '../i18n';
import { useAuthStore } from '../store/auth';

export function useAuthBootstrap() {
  const status = useAuthStore((state) => state.status);
  const setBootstrapping = useAuthStore((state) => state.setBootstrapping);
  const setAuthenticated = useAuthStore((state) => state.setAuthenticated);
  const setAnonymous = useAuthStore((state) => state.setAnonymous);
  const setInitError = useAuthStore((state) => state.setInitError);

  const query = useQuery({
    queryKey: ['auth-bootstrap'],
    queryFn: async () => {
      const health = await getHealth();
      if (!health.ready) {
        throw new Error(health.startup_error || translate('http.backendStartupIncomplete'));
      }
      try {
        const user = await getCurrentUser();
        return { health, user };
      } catch (error) {
        if (
          (error instanceof ApiError && error.status === 401) ||
          (axios.isAxiosError(error) && error.response?.status === 401)
        ) {
          return { health, user: null };
        }
        throw error;
      }
    },
    retry: 1,
    staleTime: Number.POSITIVE_INFINITY,
    gcTime: Number.POSITIVE_INFINITY,
  });

  useEffect(() => {
    if (query.isPending && status !== 'authenticated') {
      setBootstrapping();
    }
  }, [query.isPending, setBootstrapping, status]);

  useEffect(() => {
    if (!query.data) {
      return;
    }
    if (query.data.user) {
      setAuthenticated(query.data);
      return;
    }
    setAnonymous({
      health: query.data.health,
      notice:
        query.data.health.runtime_mode === 'deployed-web' ? translate('auth.loginRequired') : null,
    });
  }, [query.data, setAnonymous, setAuthenticated]);

  useEffect(() => {
    if (!query.error) {
      return;
    }
    setInitError(getErrorMessage(query.error, translate('http.initFailed')));
  }, [query.error, setInitError]);

  return query;
}

export const useBackendSession = useAuthBootstrap;
