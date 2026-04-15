from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.schemas import AuditRequest, AuditResponse
from app.services.audit import build_benchmark, run_single_audit
from app.ui import DASHBOARD_HTML

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/", response_class=HTMLResponse)
async def dashboard() -> str:
    return DASHBOARD_HTML


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}


@app.post("/api/v1/audits", response_model=AuditResponse)
async def create_audit(payload: AuditRequest) -> AuditResponse:
    if len(payload.competitor_urls) > settings.max_competitor_urls:
        raise HTTPException(
            status_code=422,
            detail=f"Max {settings.max_competitor_urls} competitor URLs are allowed per request.",
        )

    try:
        target_result = await run_single_audit(str(payload.target_url))
        competitor_results = [
            await run_single_audit(str(url)) for url in payload.competitor_urls
        ]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Audit failed: {exc}") from exc

    benchmark = build_benchmark(target_result, competitor_results)
    return AuditResponse(target=target_result, competitors=competitor_results, benchmark=benchmark)
