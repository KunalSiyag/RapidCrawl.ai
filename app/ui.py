from __future__ import annotations

DASHBOARD_HTML = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>RapidCrawl.ai | SEO & Analytics Auditor</title>
  <style>
    :root {
      --bg: #0b1020;
      --surface: #121933;
      --surface-2: #1a2345;
      --text: #eaf0ff;
      --muted: #a9b3d9;
      --good: #35d07f;
      --warn: #f4b942;
      --bad: #ff6b6b;
      --accent: #6ea8fe;
      --border: #2a3563;
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: Inter, Segoe UI, Roboto, Arial, sans-serif; background: linear-gradient(160deg, var(--bg), #0d1530 40%, #17224b); color: var(--text); }
    .wrap { max-width: 1100px; margin: 0 auto; padding: 32px 20px 80px; }
    .hero h1 { margin: 0 0 10px; font-size: 2rem; }
    .hero p { margin: 0; color: var(--muted); }

    .panel { background: rgba(18,25,51,0.85); border: 1px solid var(--border); border-radius: 14px; padding: 18px; margin-top: 20px; backdrop-filter: blur(4px); }
    label { display:block; margin-bottom: 6px; color: var(--muted); font-size: 0.92rem; }
    input, textarea, button { width: 100%; border-radius: 10px; border: 1px solid var(--border); background: var(--surface-2); color: var(--text); padding: 12px; }
    textarea { min-height: 90px; resize: vertical; }
    .grid { display:grid; grid-template-columns: 2fr 1fr; gap: 14px; }
    button { cursor: pointer; background: linear-gradient(120deg, #5d8eff, #7196ff); border: none; font-weight: 700; }

    .loading { display:none; margin-top: 10px; color: var(--accent); }
    .error { display:none; margin-top: 10px; color: var(--bad); }

    .score-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-top: 12px; }
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 12px; }
    .label { color: var(--muted); font-size: 0.85rem; }
    .big { font-size: 1.6rem; font-weight: 700; margin-top: 6px; }

    .badge { display:inline-block; padding: 5px 10px; border-radius: 999px; font-size: 0.78rem; text-transform: uppercase; letter-spacing: .03em; }
    .critical, .high { background: rgba(255,107,107,.15); color: var(--bad); }
    .medium { background: rgba(244,185,66,.15); color: var(--warn); }
    .low { background: rgba(53,208,127,.15); color: var(--good); }

    table { width:100%; border-collapse: collapse; margin-top: 10px; }
    th, td { padding: 10px; border-bottom: 1px solid var(--border); text-align:left; vertical-align: top; }
    th { color: var(--muted); font-size: 0.84rem; }
    .split { display:grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    @media (max-width: 900px) { .grid, .split { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class=\"wrap\">
    <section class=\"hero\">
      <h1>RapidCrawl.ai Audit Studio</h1>
      <p>Run SEO + analytics audits, compare competitors, and get clear prioritized improvements with business impact.</p>
    </section>

    <section class=\"panel\">
      <div class=\"grid\">
        <div>
          <label for=\"target\">Target Website URL</label>
          <input id=\"target\" placeholder=\"https://yourcompany.com\" />
        </div>
        <div style=\"align-self:end\">
          <button id=\"runAudit\">Run Audit</button>
        </div>
      </div>
      <div style=\"margin-top:12px\">
        <label for=\"competitors\">Competitor URLs (one per line, max 3 default)</label>
        <textarea id=\"competitors\" placeholder=\"https://competitor-one.com\nhttps://competitor-two.com\"></textarea>
      </div>
      <div id=\"loading\" class=\"loading\">Running crawl + analysis…</div>
      <div id=\"error\" class=\"error\"></div>
    </section>

    <section id=\"results\" style=\"display:none\">
      <div class=\"panel\">
        <h2 style=\"margin-top:0\">Audit Overview</h2>
        <p id=\"summary\" style=\"color:var(--muted); margin: 8px 0 2px;\"></p>
        <div class=\"score-grid\" id=\"scores\"></div>
      </div>

      <div class=\"split\">
        <div class=\"panel\">
          <h3 style=\"margin-top:0\">Top Findings</h3>
          <div id=\"findings\"></div>
        </div>
        <div class=\"panel\">
          <h3 style=\"margin-top:0\">Metrics</h3>
          <div id=\"metrics\"></div>
        </div>
      </div>

      <div class=\"panel\">
        <h3 style=\"margin-top:0\">Competitor Benchmark</h3>
        <p id=\"benchmarkNote\" style=\"color:var(--muted)\"></p>
        <div id=\"competitorsTable\"></div>
      </div>
    </section>
  </div>

<script>
const byId = (id) => document.getElementById(id);

function scoreCard(label, value) {
  return `<div class=\"card\"><div class=\"label\">${label}</div><div class=\"big\">${value}</div></div>`;
}

function renderFindings(findings) {
  if (!findings.length) return '<p style="color:var(--good)">No major issues detected.</p>';
  return findings
    .sort((a, b) => ({critical:0,high:1,medium:2,low:3}[a.severity] - ({critical:0,high:1,medium:2,low:3}[b.severity])))
    .slice(0, 10)
    .map(f => `
      <div class="card" style="margin-bottom:10px">
        <div style="display:flex;justify-content:space-between;gap:8px;align-items:center;">
          <strong>${f.title}</strong>
          <span class="badge ${f.severity}">${f.severity}</span>
        </div>
        <p style="color:var(--muted)"><strong>Why:</strong> ${f.why_it_matters}</p>
        <p><strong>Fix:</strong> ${f.recommendation}</p>
        <div class="label">Estimated effort: ${f.effort}</div>
      </div>
    `).join('');
}

function renderMetrics(metrics) {
  if (!metrics.length) return '<p>No metrics returned.</p>';
  const rows = metrics.map(m => `<tr><td>${m.name}</td><td>${m.value}</td><td>${m.passed ? '✅ Pass' : '⚠️ Review'}</td><td>${m.benchmark ?? '-'}</td></tr>`).join('');
  return `<table><thead><tr><th>Metric</th><th>Value</th><th>Status</th><th>Benchmark</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function renderCompetitors(competitors) {
  if (!competitors.length) return '<p style="color:var(--muted)">No competitor URLs provided.</p>';
  const rows = competitors.map(c => `<tr><td>${c.url}</td><td>${c.score}</td><td>${c.seo_score}</td><td>${c.analytics_score}</td><td>${c.technical_score}</td></tr>`).join('');
  return `<table><thead><tr><th>URL</th><th>Total</th><th>SEO</th><th>Analytics</th><th>Technical</th></tr></thead><tbody>${rows}</tbody></table>`;
}

byId('runAudit').addEventListener('click', async () => {
  const target = byId('target').value.trim();
  const competitors = byId('competitors').value
    .split('\n')
    .map(v => v.trim())
    .filter(Boolean);

  byId('error').style.display = 'none';
  byId('loading').style.display = 'block';

  try {
    const response = await fetch('/api/v1/audits', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({target_url: target, competitor_urls: competitors}),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to audit');
    }

    byId('results').style.display = 'block';
    byId('summary').innerText = `${data.target.url} — ${data.target.summary}`;

    byId('scores').innerHTML = [
      scoreCard('Total Score', data.target.score),
      scoreCard('SEO Score', data.target.seo_score),
      scoreCard('Analytics Score', data.target.analytics_score),
      scoreCard('Technical Score', data.target.technical_score),
      scoreCard('Findings', data.target.findings.length),
      scoreCard('Metric Checks', data.target.metrics.length)
    ].join('');

    byId('findings').innerHTML = renderFindings(data.target.findings);
    byId('metrics').innerHTML = renderMetrics(data.target.metrics);
    byId('benchmarkNote').innerText = data.benchmark.note;
    byId('competitorsTable').innerHTML = renderCompetitors(data.competitors);
  } catch (err) {
    byId('error').innerText = err.message;
    byId('error').style.display = 'block';
  } finally {
    byId('loading').style.display = 'none';
  }
});
</script>
</body>
</html>
"""
