const operatingSignals = [
  { label: 'Active sessions', value: '08' },
  { label: 'Transfer lanes', value: 'SFTP / SCP / Parallel' },
  { label: 'Boundary mode', value: 'remote_root' },
];

const productPillars = [
  {
    title: 'Multi-session workspace',
    body: 'Open several SSH destinations at once, compare remote panels side by side, and move files without losing operational context.',
  },
  {
    title: 'Visible transfer control',
    body: 'Pause, resume, cancel, retry, and inspect progress from one task center built for large-file and folder operations.',
  },
  {
    title: 'Safer remote boundaries',
    body: 'Use remote roots, least-privilege accounts, and explicit saved-site scopes to keep everyday transfer work constrained.',
  },
];

const workflowSteps = ['Connect', 'Stage', 'Transfer', 'Verify'];

export function LandingPage() {
  return (
    <main className="landing-page">
      <header className="landing-nav" aria-label="SSHFerry homepage navigation">
        <a href="/" className="landing-brand" aria-label="SSHFerry home">
          <span className="landing-brand-mark" aria-hidden="true">
            SF
          </span>
          <span>SSHFerry</span>
        </a>
        <nav className="landing-nav-links" aria-label="Homepage links">
          <a href="#capabilities">Capabilities</a>
          <a href="#workflow">Workflow</a>
          <a href="/login">Log in</a>
        </nav>
      </header>

      <section className="landing-hero">
        <div className="landing-hero-copy">
          <p className="landing-kicker">Secure SSH file operations for modern teams</p>
          <h1>SSHFerry</h1>
          <p className="landing-lede">
            A commercial-grade workspace for controlled uploads, downloads, remote-to-remote copy, and
            high-visibility transfer operations across SSH environments.
          </p>
          <div className="landing-actions">
            <a href="/login" className="landing-primary-action">
              Enter Workspace
            </a>
            <a href="/signup" className="landing-secondary-action">
              Create Account
            </a>
          </div>
        </div>

        <div className="landing-visual" aria-label="SSHFerry product transfer workspace preview">
          <div className="landing-command-strip">
            <span>sshferry.cloud</span>
            <span>secured session fabric</span>
          </div>
          <div className="landing-transfer-map">
            <div className="landing-node landing-node-source">
              <strong>Origin</strong>
              <span>/releases</span>
            </div>
            <div className="landing-transfer-path" aria-hidden="true">
              <span />
              <span />
              <span />
            </div>
            <div className="landing-node landing-node-target">
              <strong>Remote</strong>
              <span>/deploy</span>
            </div>
          </div>
          <div className="landing-preview-grid">
            {operatingSignals.map((signal) => (
              <div className="landing-signal" key={signal.label}>
                <span>{signal.label}</span>
                <strong>{signal.value}</strong>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="landing-band landing-proof-band" aria-label="Operational highlights">
        <div>
          <span className="landing-proof-index">01</span>
          <p>Designed around real SSH file work, not generic storage dashboards.</p>
        </div>
        <div>
          <span className="landing-proof-index">02</span>
          <p>Task visibility is built into the transfer path from the first operation.</p>
        </div>
        <div>
          <span className="landing-proof-index">03</span>
          <p>Workspace and remote panels keep daily operations bounded and repeatable.</p>
        </div>
      </section>

      <section className="landing-section" id="capabilities">
        <div className="landing-section-head">
          <p className="landing-kicker">Capabilities</p>
          <h2>Built for repeated remote file operations</h2>
        </div>
        <div className="landing-pillar-grid">
          {productPillars.map((pillar) => (
            <article className="landing-pillar" key={pillar.title}>
              <h3>{pillar.title}</h3>
              <p>{pillar.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="landing-section landing-workflow" id="workflow">
        <div className="landing-section-head">
          <p className="landing-kicker">Workflow</p>
          <h2>One operational path from connection to verification</h2>
        </div>
        <ol className="landing-workflow-steps">
          {workflowSteps.map((step, index) => (
            <li key={step}>
              <span>{String(index + 1).padStart(2, '0')}</span>
              <strong>{step}</strong>
            </li>
          ))}
        </ol>
      </section>

      <section className="landing-cta" aria-label="Start using SSHFerry">
        <div>
          <p className="landing-kicker">Workspace ready</p>
          <h2>Move from scattered terminal transfers to a controlled SSH operations surface.</h2>
        </div>
        <a href="/login" className="landing-primary-action">
          Enter Workspace
        </a>
      </section>
    </main>
  );
}
