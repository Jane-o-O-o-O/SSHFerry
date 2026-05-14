import { createBrowserRouter, Navigate } from 'react-router-dom';

import { OwnerRoute } from '../components/auth/OwnerRoute';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';
import { BootstrapPage } from '../pages/bootstrap/BootstrapPage';
import { RouteErrorPage } from '../pages/error/RouteErrorPage';
import { LandingPage } from '../pages/landing/LandingPage';
import { LoginPage } from '../pages/login/LoginPage';
import { SignUpPage } from '../pages/login/SignUpPage';
import { LogsPage } from '../pages/logs/LogsPage';
import { ActivityPage } from '../pages/activity/ActivityPage';
import { TasksPage } from '../pages/tasks/TasksPage';
import { WorkspacePage } from '../pages/workspace/WorkspacePage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <LandingPage />,
    errorElement: <RouteErrorPage />,
  },
  {
    path: '/login',
    element: <LoginPage />,
    errorElement: <RouteErrorPage />,
  },
  {
    path: '/signup',
    element: <SignUpPage />,
    errorElement: <RouteErrorPage />,
  },
  {
    path: '/workspace',
    element: (
      <ProtectedRoute>
        <WorkspacePage />
      </ProtectedRoute>
    ),
    errorElement: <RouteErrorPage />,
  },
  {
    path: '/tasks',
    element: (
      <ProtectedRoute>
        <TasksPage />
      </ProtectedRoute>
    ),
    errorElement: <RouteErrorPage />,
  },
  {
    path: '/logs',
    element: (
      <ProtectedRoute>
        <ActivityPage />
      </ProtectedRoute>
    ),
    errorElement: <RouteErrorPage />,
  },
  {
    path: '/debug/logs',
    element: (
      <OwnerRoute>
        <LogsPage />
      </OwnerRoute>
    ),
    errorElement: <RouteErrorPage />,
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);
