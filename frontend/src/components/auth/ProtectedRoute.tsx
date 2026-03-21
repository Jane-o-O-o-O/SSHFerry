import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

import { useI18n } from '../../i18n';
import { useAuthStore } from '../../store/auth';

interface ProtectedRouteProps {
  children: ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const location = useLocation();
  const status = useAuthStore((state) => state.status);
  const { t } = useI18n();

  if (status === 'authenticated') {
    return <>{children}</>;
  }

  if (status === 'error') {
    return <Navigate to="/" replace />;
  }

  if (status === 'anonymous') {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return (
    <main className="bootstrap-page">
      <section className="bootstrap-panel">
        <div className="eyebrow">{t('nav.workspace')}</div>
        <h1>{t('workspace.waitTitle')}</h1>
        <p>{t('workspace.waitDescription')}</p>
      </section>
    </main>
  );
}
