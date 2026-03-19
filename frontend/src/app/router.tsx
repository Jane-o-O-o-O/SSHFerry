import { createBrowserRouter, Navigate } from 'react-router-dom';

import { OwnerRoute } from '../components/auth/OwnerRoute';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';
import { BootstrapPage } from '../pages/bootstrap/BootstrapPage';
import { LoginPage } from '../pages/login/LoginPage';
import { LogsPage } from '../pages/logs/LogsPage';
import { ActivityPage } from '../pages/activity/ActivityPage';
import { TasksPage } from '../pages/tasks/TasksPage';
import { WorkspacePage } from '../pages/workspace/WorkspacePage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <BootstrapPage />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/workspace',
    element: (
      <ProtectedRoute>
        <WorkspacePage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/tasks',
    element: (
      <ProtectedRoute>
        <TasksPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/logs',
    element: (
      <ProtectedRoute>
        <ActivityPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/debug/logs',
    element: (
      <OwnerRoute>
        <LogsPage />
      </OwnerRoute>
    ),
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);
