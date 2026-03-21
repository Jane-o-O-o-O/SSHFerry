import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

import { useI18n } from '../../i18n';
import { useAuthStore } from '../../store/auth';

interface OwnerRouteProps {
  children: ReactNode;
}

export function OwnerRoute({ children }: OwnerRouteProps) {
  const location = useLocation();
  const status = useAuthStore((state) => state.status);
  const user = useAuthStore((state) => state.user);
  const { t } = useI18n();

  if (status === 'authenticated' && user?.role === 'owner') {
    return <>{children}</>;
  }

  if (status === 'authenticated') {
    return <Navigate to="/logs" replace state={{ from: location }} />;
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
        <div className="eyebrow">{t('nav.debugLogs')}</div>
        <h1>{t('workspace.waitTitle')}</h1>
        <p>{t('workspace.waitDescription')}</p>
      </section>
    </main>
  );
}
