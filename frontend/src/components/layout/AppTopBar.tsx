import { Link, useLocation, useNavigate } from 'react-router-dom';

import { logout } from '../../api/auth';
import { useI18n } from '../../i18n';
import { useAuthStore } from '../../store/auth';
import { useTasksStore } from '../../store/tasks';
import { useUiStore } from '../../store/ui';
import { StatusBadge } from '../common/StatusBadge';

function getSocketTone(status: string) {
  if (status === 'connected') {
    return 'success' as const;
  }
  if (status === 'polling' || status === 'reconnecting') {
    return 'warning' as const;
  }
  if (status === 'error') {
    return 'danger' as const;
  }
  return 'neutral' as const;
}

export function AppTopBar() {
  const navigate = useNavigate();
  const location = useLocation();
  const health = useAuthStore((state) => state.health);
  const user = useAuthStore((state) => state.user);
  const markUnauthenticated = useAuthStore((state) => state.markUnauthenticated);
  const socketStatus = useTasksStore((state) => state.socketStatus);
  const protocolOverride = useUiStore((state) => state.protocolOverride);
  const { formatProtocol, formatSocketStatus, language, setLanguage, t } = useI18n();

  async function handleLogout() {
    try {
      await logout();
    } finally {
      markUnauthenticated(t('auth.loggedOut'));
      if (typeof window !== 'undefined') {
        window.location.assign('/login');
        return;
      }
      navigate('/login', { replace: true });
    }
  }

  return (
    <header className="topbar">
      <div className="topbar-brand">
        <strong>SSHFerry</strong>
        <span>{t('topbar.tagline')}</span>
      </div>
      <div className="topbar-statuses">
        <div className="topbar-status-item">
          <span>{t('topbar.backend')}</span>
          <StatusBadge tone={health?.ready ? 'success' : 'warning'}>
            {health?.ready ? t('common.ready') : t('common.booting')}
          </StatusBadge>
        </div>
        <div className="topbar-status-item">
          <span>{t('topbar.taskChannel')}</span>
          <StatusBadge tone={getSocketTone(socketStatus)}>{formatSocketStatus(socketStatus)}</StatusBadge>
        </div>
        <div className="topbar-status-item">
          <span>{t('topbar.protocol')}</span>
          <StatusBadge tone={protocolOverride === 'auto' ? 'neutral' : 'info'}>{formatProtocol(protocolOverride)}</StatusBadge>
        </div>
        {user ? (
          <div className="topbar-status-item">
            <span>{t('topbar.user')}</span>
            <StatusBadge tone="info">{`${user.display_name} (${user.role})`}</StatusBadge>
          </div>
        ) : null}
      </div>
      <div className="topbar-controls">
        <div className="locale-switch" role="group" aria-label={t('topbar.language')}>
          <button
            type="button"
            className={`locale-button ${language === 'zh' ? 'is-active' : ''}`}
            onClick={() => setLanguage('zh')}
          >
            {t('language.zh')}
          </button>
          <button
            type="button"
            className={`locale-button ${language === 'en' ? 'is-active' : ''}`}
            onClick={() => setLanguage('en')}
          >
            {t('language.en')}
          </button>
        </div>
        <nav className="topbar-nav">
          <Link className={location.pathname === '/workspace' ? 'nav-link active' : 'nav-link'} to="/workspace">
            {t('nav.workspace')}
          </Link>
          <Link className={location.pathname === '/tasks' ? 'nav-link active' : 'nav-link'} to="/tasks">
            {t('nav.tasks')}
          </Link>
          <Link className={location.pathname === '/logs' ? 'nav-link active' : 'nav-link'} to="/logs">
            {t('nav.logs')}
          </Link>
        </nav>
        {health?.runtime_mode === 'deployed-web' ? (
          <button type="button" className="ghost-button" onClick={() => void handleLogout()}>
            {t('auth.logout')}
          </button>
        ) : null}
      </div>
    </header>
  );
}
