# RapidCrawl.ai

Professional-grade SaaS API foundation for **SEO + analytics auditing** with prioritized recommendations and competitor benchmarking.

## What this provides

- FastAPI backend ready for SaaS productization.
- Built-in GUI dashboard at `/` for non-technical users to run audits and review findings cleanly.
- URL auditing for:
  - On-page SEO quality (title/meta/H1/canonical/alt text)
  - Analytics stack maturity (GA4, GTM, privacy tooling, legacy UA detection)
  - Technical SEO fundamentals (HTTPS, viewport, link architecture)
- Weighted scoring and prioritized findings including:
  - Why issue matters
  - Impact/severity
  - Recommended fix
  - Estimated effort
- Competitor benchmarking (best score + gap to close).

## API

### Dashboard GUI

Open `http://localhost:8000/` in your browser to use the visual audit workspace.

### Health

```bash
curl -s http://localhost:8000/health
```

### Run audit

```bash
curl -s -X POST http://localhost:8000/api/v1/audits \
  -H "content-type: application/json" \
  -d '{
    "target_url": "https://example.com",
    "competitor_urls": ["https://www.wikipedia.org", "https://www.python.org"]
  }'
```

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker

```bash
docker compose up --build
```

## Quality gates (recommended for CI)

```bash
pytest -q
```

## Next production steps

- Add authentication, tenant separation, billing, and API keys.
- Add async job queue (Celery/RQ/SQS) for multi-page and scheduled crawls.
- Persist audits in Postgres + object storage snapshots.
- Add JS-rendered crawling (Playwright) for SPA websites.
- Add GSC/GA4 integrations and anomaly detection.
