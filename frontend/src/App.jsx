import { useState } from 'react';

const API_BASE = import.meta.env.PROD ? '' : '';

const STEP_META = {
  signal_harvester: { icon: '📡', title: 'Signal Capture', desc: 'Fetching live buyer signals from Finnhub, ATS, GNews...' },
  research_analyst: { icon: '🔬', title: 'Research Analysis', desc: 'AI analyzing signals & generating Account Brief...' },
  outreach_sender: { icon: '📧', title: 'Outreach Delivery', desc: 'Generating personalized email & sending...' },
};

export default function App() {
  const [form, setForm] = useState({
    icp: '',
    company: '',
    domain: '',
    recipient_email: '',
  });
  const [loading, setLoading] = useState(false);
  const [steps, setSteps] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [expandedSteps, setExpandedSteps] = useState({});

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSteps([]);
    setResult(null);
    setError('');
    setExpandedSteps({});

    // Initialize steps as pending
    setSteps([
      { key: 'signal_harvester', status: 'pending', data: null },
      { key: 'research_analyst', status: 'pending', data: null },
      { key: 'outreach_sender', status: 'pending', data: null },
    ]);

    try {
      const response = await fetch(`${API_BASE}/api/outreach/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6));

              if (event.step === 'complete') {
                setLoading(false);
                continue;
              }

              setSteps((prev) =>
                prev.map((s) =>
                  s.key === event.step
                    ? {
                        ...s,
                        status: event.status,
                        data: event.data || s.data,
                      }
                    : s
                )
              );

              // Capture final results
              if (event.step === 'research_analyst' && event.status === 'completed') {
                setResult((prev) => ({
                  ...prev,
                  accountBrief: event.data?.account_brief || '',
                }));
              }

              if (event.step === 'outreach_sender' && event.status === 'completed') {
                setResult((prev) => ({
                  ...prev,
                  emailSubject: event.data?.subject || '',
                  emailBody: event.data?.body || '',
                  emailStatus: event.data?.status || 'unknown',
                  emailMessage: event.data?.message || '',
                }));
              }
            } catch (err) {
              // Skip malformed events
            }
          }
        }
      }
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (key) => {
    setExpandedSteps((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const getIndicatorClass = (status) => {
    return `step__indicator step__indicator--${status}`;
  };

  const getIndicatorSymbol = (status) => {
    switch (status) {
      case 'running': return '⟳';
      case 'completed': return '✓';
      case 'error': return '✗';
      default: return '·';
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="header__logo">
          <div className="header__icon">🔥</div>
          <h1 className="header__title">FireReach</h1>
        </div>
        <p className="header__subtitle">
          Autonomous outreach engine that captures live buyer signals,
          generates research briefs, and sends hyper-personalized emails.
        </p>
        <span className="header__badge">Rabbitt AI Ecosystem</span>
      </header>

      {/* Input Form */}
      <section className="card" style={{ marginBottom: '2rem' }}>
        <div className="card__title">
          <span className="card__title-icon">🎯</span>
          Configure Outreach
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group form-group--full">
              <label className="form-label" htmlFor="icp">
                Ideal Customer Profile (ICP)
              </label>
              <textarea
                id="icp"
                className="form-textarea"
                placeholder='e.g. "We sell high-end cybersecurity training to Series B startups."'
                value={form.icp}
                onChange={(e) => setForm({ ...form, icp: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="company">
                Target Company
              </label>
              <input
                id="company"
                className="form-input"
                placeholder="e.g. CrowdStrike"
                value={form.company}
                onChange={(e) => setForm({ ...form, company: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="domain">
                Company Domain
              </label>
              <input
                id="domain"
                className="form-input"
                placeholder="e.g. crowdstrike.com"
                value={form.domain}
                onChange={(e) => setForm({ ...form, domain: e.target.value })}
              />
            </div>

            <div className="form-group form-group--full">
              <label className="form-label" htmlFor="email">
                Recipient Email
              </label>
              <input
                id="email"
                className="form-input"
                type="email"
                placeholder="candidate@example.com"
                value={form.recipient_email}
                onChange={(e) =>
                  setForm({ ...form, recipient_email: e.target.value })
                }
                required
              />
            </div>
          </div>

          <button
            className="btn-primary"
            type="submit"
            disabled={loading}
          >
            {loading && <span className="spinner" />}
            {loading ? 'Agent Running...' : '🚀 Launch Outreach Agent'}
          </button>
        </form>
      </section>

      {/* Pipeline Steps */}
      {steps.length > 0 && (
        <section className="pipeline card">
          <div className="card__title">
            <span className="card__title-icon">⚡</span>
            Agent Pipeline
          </div>

          <div className="pipeline__steps">
            {steps.map((step, idx) => {
              const meta = STEP_META[step.key] || {};
              return (
                <div
                  key={step.key}
                  className={`step ${step.status === 'running' ? 'step--active' : ''}`}
                >
                  <div className={getIndicatorClass(step.status)}>
                    {getIndicatorSymbol(step.status)}
                  </div>

                  <div className="step__content">
                    <div className="step__title">
                      {meta.icon} {meta.title}
                    </div>
                    <div className="step__description">
                      {step.status === 'completed'
                        ? 'Completed successfully'
                        : step.status === 'running'
                        ? meta.desc
                        : 'Waiting...'}
                    </div>

                    {step.data && step.status === 'completed' && (
                      <div className="step__data">
                        {/* Signal tags for harvester */}
                        {step.key === 'signal_harvester' && step.data?.signals && (
                          <div className="signal-tags">
                            {Object.entries(step.data.signals).map(([key, val]) => {
                              const hasData =
                                val?.data &&
                                (typeof val.data === 'object'
                                  ? !val.data.error && !val.data.note
                                  : true);
                              return (
                                <span
                                  key={key}
                                  className={`signal-tag ${hasData ? 'signal-tag--has-data' : ''}`}
                                >
                                  {hasData ? '●' : '○'} {key}
                                </span>
                              );
                            })}
                          </div>
                        )}

                        <button
                          className="step__data-toggle"
                          style={{ marginTop: '0.75rem' }}
                          onClick={() => toggleExpand(step.key)}
                        >
                          {expandedSteps[step.key]
                            ? '▲ Hide Raw Data'
                            : '▼ View Raw Data'}
                        </button>

                        {expandedSteps[step.key] && (
                          <div className="json-viewer">
                            {JSON.stringify(step.data, null, 2)}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Results */}
      {result && (
        <section className="result-section">
          {/* Account Brief */}
          {result.accountBrief && (
            <div className="result-card result-card--brief">
              <div className="result-card__header">🔬 Account Brief</div>
              <div className="result-card__body">{result.accountBrief}</div>
            </div>
          )}

          {/* Email */}
          {result.emailBody && (
            <div className="result-card result-card--email">
              <div className="result-card__header">
                📧 Generated Email
                <span
                  className={`status-badge status-badge--${result.emailStatus}`}
                  style={{ marginLeft: 'auto' }}
                >
                  ● {result.emailStatus}
                </span>
              </div>
              {result.emailSubject && (
                <div className="email-subject">
                  Subject: {result.emailSubject}
                </div>
              )}
              <div className="result-card__body">{result.emailBody}</div>
              {result.emailMessage && (
                <p
                  style={{
                    marginTop: '1rem',
                    fontSize: '0.8rem',
                    color: 'var(--text-muted)',
                  }}
                >
                  {result.emailMessage}
                </p>
              )}
            </div>
          )}
        </section>
      )}

      {/* Error */}
      {error && (
        <div
          className="card"
          style={{
            marginTop: '2rem',
            borderColor: 'var(--error)',
            color: 'var(--error)',
          }}
        >
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Footer */}
      <footer className="footer">
        <p>
          Built with 🔥 for the{' '}
          <a
            href="https://rabbitt.ai"
            target="_blank"
            rel="noopener noreferrer"
          >
            Rabbitt AI
          </a>{' '}
          Ecosystem
        </p>
      </footer>
    </div>
  );
}
