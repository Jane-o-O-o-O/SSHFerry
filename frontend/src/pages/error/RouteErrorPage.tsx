import { isRouteErrorResponse, useNavigate, useRouteError } from 'react-router-dom';

import { useI18n } from '../../i18n';

const COPY = {
  zh: {
    title: '\u9875\u9762\u53d1\u751f\u5f02\u5e38',
    description:
      '\u5f53\u524d\u9875\u9762\u9047\u5230\u4e86\u672a\u5904\u7406\u7684\u524d\u7aef\u9519\u8bef\u3002\u4f60\u53ef\u4ee5\u5148\u8fd4\u56de\u9996\u9875\u3001\u91cd\u65b0\u8fdb\u5165\u5de5\u4f5c\u533a\uff0c\u6216\u8005\u76f4\u63a5\u5237\u65b0\u9875\u9762\u3002',
    home: '\u56de\u5230\u9996\u9875',
    workspace: '\u6253\u5f00\u5de5\u4f5c\u533a',
    retry: '\u91cd\u65b0\u52a0\u8f7d',
  },
  en: {
    title: 'This page hit an unexpected error',
    description: 'An unhandled frontend error interrupted the current route. You can go home, reopen the workspace, or reload the page.',
    home: 'Back Home',
    workspace: 'Open Workspace',
    retry: 'Reload',
  },
} as const;

function resolveRouteErrorMessage(error: unknown): string | null {
  if (isRouteErrorResponse(error)) {
    if (typeof error.data === 'string' && error.data.trim()) {
      return error.data;
    }
    return error.statusText || null;
  }

  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === 'string' && error.trim()) {
    return error;
  }

  return null;
}

export function RouteErrorPage() {
  const error = useRouteError();
  const navigate = useNavigate();
  const { language, t } = useI18n();
  const copy = COPY[language];
  const detail = resolveRouteErrorMessage(error);

  return (
    <main className="bootstrap-page">
      <section className="bootstrap-panel">
        <div className="eyebrow">{t('app.title')}</div>
        <h1>{copy.title}</h1>
        <p>{copy.description}</p>
        {detail ? <p className="bootstrap-error">{detail}</p> : null}
        <div className="login-actions">
          <button type="button" className="ghost-button" onClick={() => navigate('/', { replace: true })}>
            {copy.home}
          </button>
          <button type="button" className="ghost-button" onClick={() => navigate('/workspace', { replace: true })}>
            {copy.workspace}
          </button>
          <button type="button" className="primary-button" onClick={() => window.location.reload()}>
            {copy.retry}
          </button>
        </div>
      </section>
    </main>
  );
}
