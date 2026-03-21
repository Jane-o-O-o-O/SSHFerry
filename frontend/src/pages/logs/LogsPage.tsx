import { AppTopBar } from '../../components/layout/AppTopBar';
import { LogPlaceholder } from '../../components/logs/LogPlaceholder';
import { useLogSocket } from '../../hooks/useLogSocket';

export function LogsPage() {
  useLogSocket();

  return (
    <main className="app-shell">
      <AppTopBar />
      <section className="content-page-shell logs-page-shell">
        <LogPlaceholder fullPage />
      </section>
    </main>
  );
}
