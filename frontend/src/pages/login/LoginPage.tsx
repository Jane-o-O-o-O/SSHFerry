import { useEffect, useMemo, useState, type FormEvent } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import { getHealth, login } from '../../api/auth';
import { getErrorMessage } from '../../api/http';
import { useI18n } from '../../i18n';
import { useAuthStore } from '../../store/auth';

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const status = useAuthStore((state) => state.status);
  const health = useAuthStore((state) => state.health);
  const authNotice = useAuthStore((state) => state.authNotice);
  const setAuthenticated = useAuthStore((state) => state.setAuthenticated);
  const clearAuthNotice = useAuthStore((state) => state.clearAuthNotice);
  const { t } = useI18n();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const redirectTarget = useMemo(() => {
    const state = location.state as { from?: { pathname?: string } } | null;
    return state?.from?.pathname || '/workspace';
  }, [location.state]);

  useEffect(() => {
    if (status === 'authenticated') {
      navigate(redirectTarget, { replace: true });
    }
  }, [navigate, redirectTarget, status]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    try {
      const user = await login({ username, password });
      const latestHealth = health ?? (await getHealth());
      setAuthenticated({ health: latestHealth, user });
      clearAuthNotice();
      navigate(redirectTarget, { replace: true });
    } catch (error) {
      setFormError(getErrorMessage(error, t('auth.loginFailed')));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="bootstrap-page login-page">
      <section className="bootstrap-panel login-panel">
        <div className="eyebrow">{t('brand.frontend')}</div>
        <h1>{t('login.title')}</h1>
        <p>{t('login.description')}</p>
        {authNotice ? <div className="login-notice">{authNotice}</div> : null}
        {formError ? <div className="bootstrap-error login-error">{formError}</div> : null}
        <form className="login-form" onSubmit={handleSubmit}>
          <label className="form-field">
            <span>{t('login.username')}</span>
            <input
              autoComplete="username"
              name="username"
              placeholder={t('login.usernamePlaceholder')}
              value={username}
              onChange={(event) => setUsername(event.target.value)}
            />
          </label>
          <label className="form-field">
            <span>{t('login.password')}</span>
            <input
              autoComplete="current-password"
              name="password"
              type="password"
              placeholder={t('login.passwordPlaceholder')}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          <div className="login-actions">
            <button type="submit" className="primary-button" disabled={submitting}>
              {submitting ? t('login.submitting') : t('login.submit')}
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}

