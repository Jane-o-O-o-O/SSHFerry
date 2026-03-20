import { useEffect, useMemo, useState, type FormEvent } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

import { getHealth, signup } from '../../api/auth';
import { getErrorMessage } from '../../api/http';
import { useI18n } from '../../i18n';
import { useAuthStore } from '../../store/auth';

export function SignUpPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const status = useAuthStore((state) => state.status);
  const health = useAuthStore((state) => state.health);
  const setAuthenticated = useAuthStore((state) => state.setAuthenticated);
  const clearAuthNotice = useAuthStore((state) => state.clearAuthNotice);
  const { language, setLanguage, t } = useI18n();

  const [username, setUsername] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
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
    if (password !== confirmPassword) {
      setFormError(t('signup.passwordMismatch'));
      return;
    }
    setSubmitting(true);
    setFormError(null);
    try {
      const user = await signup({ username, password, display_name: displayName || null });
      const latestHealth = health ?? (await getHealth());
      setAuthenticated({ health: latestHealth, user });
      clearAuthNotice();
      navigate(redirectTarget, { replace: true });
    } catch (error) {
      setFormError(getErrorMessage(error, t('signup.failed')));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="bootstrap-page login-page">
      <section className="bootstrap-panel login-panel">
        <div className="bootstrap-panel-toolbar">
          <div className="eyebrow">{t('brand.frontend')}</div>
          <div className="locale-switch locale-switch-compact" role="group" aria-label={t('topbar.language')}>
            <button type="button" className={`locale-button ${language === 'zh' ? 'is-active' : ''}`} onClick={() => setLanguage('zh')}>
              {t('language.zh')}
            </button>
            <button type="button" className={`locale-button ${language === 'en' ? 'is-active' : ''}`} onClick={() => setLanguage('en')}>
              {t('language.en')}
            </button>
          </div>
        </div>
        <h1>{t('signup.title')}</h1>
        <p>{t('signup.description')}</p>
        {formError ? <div className="bootstrap-error login-error">{formError}</div> : null}
        <form className="login-form" onSubmit={handleSubmit}>
          <label className="form-field">
            <span>{t('signup.username')}</span>
            <input autoComplete="username" name="username" placeholder={t('signup.usernamePlaceholder')} value={username} onChange={(event) => setUsername(event.target.value)} />
          </label>
          <label className="form-field">
            <span>{t('signup.displayName')}</span>
            <input autoComplete="nickname" name="displayName" placeholder={t('signup.displayNamePlaceholder')} value={displayName} onChange={(event) => setDisplayName(event.target.value)} />
          </label>
          <label className="form-field">
            <span>{t('signup.password')}</span>
            <input autoComplete="new-password" name="password" type="password" placeholder={t('signup.passwordPlaceholder')} value={password} onChange={(event) => setPassword(event.target.value)} />
          </label>
          <label className="form-field">
            <span>{t('signup.confirmPassword')}</span>
            <input autoComplete="new-password" name="confirmPassword" type="password" placeholder={t('signup.confirmPasswordPlaceholder')} value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} />
          </label>
          <div className="login-actions">
            <button type="submit" className="primary-button" disabled={submitting}>
              {submitting ? t('signup.submitting') : t('signup.submit')}
            </button>
          </div>
        </form>
        <p>
          {t('signup.switchPrompt')} <Link to="/login">{t('signup.switchAction')}</Link>
        </p>
      </section>
    </main>
  );
}
