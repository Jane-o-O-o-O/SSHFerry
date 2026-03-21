import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import { useI18n } from '../../i18n';
import { useAuthStore } from '../../store/auth';

export function BootstrapPage() {
  const navigate = useNavigate();
  const status = useAuthStore((state) => state.status);
  const error = useAuthStore((state) => state.initError);
  const { language, setLanguage, t } = useI18n();

  useEffect(() => {
    if (status === 'authenticated') {
      navigate('/workspace', { replace: true });
      return;
    }
    if (status === 'anonymous') {
      navigate('/login', { replace: true });
    }
  }, [navigate, status]);

  return (
    <main className="bootstrap-page">
      <section className="bootstrap-panel">
        <div className="bootstrap-panel-toolbar">
          <div className="eyebrow">{t('brand.frontend')}</div>
          <div className="locale-switch locale-switch-compact" role="group" aria-label={t('topbar.language')}>
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
        </div>
        <h1>{t('bootstrap.title')}</h1>
        {status === 'error' ? (
          <>
            <p className="bootstrap-error">{error || t('bootstrap.error')}</p>
            <button type="button" className="primary-button" onClick={() => window.location.reload()}>
              {t('bootstrap.retry')}
            </button>
          </>
        ) : (
          <>
            <p>{t('bootstrap.description')}</p>
            <div className="bootstrap-progress">
              <span className="progress-ping" />
              <span>{status === 'authenticated' ? t('bootstrap.complete') : t('bootstrap.connecting')}</span>
            </div>
          </>
        )}
      </section>
    </main>
  );
}