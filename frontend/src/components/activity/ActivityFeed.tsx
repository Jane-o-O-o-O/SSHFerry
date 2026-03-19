import { useEffect, useRef, useState } from 'react';

import { useI18n } from '../../i18n';
import { useActivityStore } from '../../store/activity';
import { StatusBadge } from '../common/StatusBadge';

interface ActivityFeedProps {
  fullPage?: boolean;
}

function getActivityTone(level: string) {
  if (level === 'error') {
    return 'danger' as const;
  }
  if (level === 'warning') {
    return 'warning' as const;
  }
  if (level === 'success') {
    return 'success' as const;
  }
  return 'info' as const;
}

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

const categoryKeyMap: Record<string, string> = {
  auth: 'activity.category.auth',
  site: 'activity.category.site',
  session: 'activity.category.session',
  workspace: 'activity.category.workspace',
  remote: 'activity.category.remote',
  task: 'activity.category.task',
  system: 'activity.category.system',
};

export function ActivityFeed({ fullPage = false }: ActivityFeedProps) {
  const items = useActivityStore((state) => state.items);
  const total = useActivityStore((state) => state.total);
  const socketStatus = useActivityStore((state) => state.socketStatus);
  const socketError = useActivityStore((state) => state.socketError);
  const listRef = useRef<HTMLDivElement | null>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const { formatDateTime, formatSocketStatus, t } = useI18n();

  useEffect(() => {
    if (!autoScroll || !listRef.current) {
      return;
    }
    listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [autoScroll, items, fullPage]);

  return (
    <section className={`activity-feed ${fullPage ? 'activity-feed-full' : ''} panel-shell`}>
      <header className="panel-header">
        <div>
          <h3>{t('activity.title')}</h3>
          <p>{t(fullPage ? 'activity.pageDescription' : 'activity.description')}</p>
        </div>
        <div className="panel-actions">
          <StatusBadge tone={getSocketTone(socketStatus)}>{formatSocketStatus(socketStatus)}</StatusBadge>
        </div>
      </header>
      <div className="log-toolbar">
        <div className="log-toolbar-meta">
          <span className="mono-cell">{t('activity.summary', { total })}</span>
          {socketError ? <span className="inline-error">{socketError}</span> : null}
        </div>
        <div className="log-toolbar-actions">
          <label className="log-auto-scroll">
            <input type="checkbox" checked={autoScroll} onChange={(event) => setAutoScroll(event.target.checked)} />
            {t('activity.autoScroll')}
          </label>
        </div>
      </div>
      <div className="log-viewer-body">
        {!items.length ? (
          <div className="table-state log-empty">
            <strong>{t('activity.emptyTitle')}</strong>
            <p>{t('activity.emptyBody')}</p>
          </div>
        ) : (
          <div className="activity-list" ref={listRef}>
            {items.map((item) => {
              const categoryKey = categoryKeyMap[item.category];
              return (
                <article key={item.sequence} className="activity-entry">
                  <div className="activity-entry-head">
                    <span className="mono-cell">{formatDateTime(item.timestamp)}</span>
                    <StatusBadge tone={getActivityTone(item.level)}>{item.level}</StatusBadge>
                    <StatusBadge tone="neutral">{categoryKey ? t(categoryKey) : item.category}</StatusBadge>
                  </div>
                  <div className="activity-title">{item.title}</div>
                  <div className="activity-message">{item.message}</div>
                </article>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}
