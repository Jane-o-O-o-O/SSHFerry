import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider } from 'react-router-dom';

import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { ToastViewport } from '../components/common/ToastViewport';
import { useAuthBootstrap } from '../hooks/useBackendSession';
import { useActivitySocket } from '../hooks/useActivitySocket';
import { useTaskSocket } from '../hooks/useTaskSocket';
import { useWorkspaceBootstrap } from '../hooks/useWorkspaceBootstrap';
import { I18nProvider } from '../i18n';
import { router } from './router';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
    mutations: {
      retry: 0,
    },
  },
});

function AppRuntime() {
  useAuthBootstrap();
  useWorkspaceBootstrap();
  useTaskSocket();
  useActivitySocket();
  return null;
}

export function AppProviders() {
  return (
    <QueryClientProvider client={queryClient}>
      <I18nProvider>
        <AppRuntime />
        <RouterProvider router={router} />
        <ConfirmDialog />
        <ToastViewport />
      </I18nProvider>
    </QueryClientProvider>
  );
}
