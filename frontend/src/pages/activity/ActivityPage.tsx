import { AppTopBar } from '../../components/layout/AppTopBar';
import { ActivityFeed } from '../../components/activity/ActivityFeed';

export function ActivityPage() {
  return (
    <main className="app-shell">
      <AppTopBar />
      <section className="content-page-shell activity-page-shell">
        <ActivityFeed fullPage />
      </section>
    </main>
  );
}
