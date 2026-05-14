import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import { I18nProvider } from '../../i18n';
import { LandingPage } from './LandingPage';

describe('LandingPage', () => {
  it('renders the commercial homepage with workspace entry links', () => {
    const html = renderToStaticMarkup(
      <I18nProvider>
        <LandingPage />
      </I18nProvider>,
    );

    expect(html).toContain('SSHFerry');
    expect(html).toContain('Enter Workspace');
    expect(html).toContain('Secure SSH file operations');
    expect(html).toContain('href="/login"');
    expect(html).toContain('href="/signup"');
    expect(html).toContain('contact@sshferry.cloud');
    expect(html).toContain('Sample operations panel');
    expect(html).toContain('2.8 TB');
  });
});
