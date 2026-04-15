from __future__ import annotations

from app.core.config import settings
from app.schemas import AuditResult, BenchmarkSummary
from app.services.analyzers import analyze_page
from app.services.fetcher import fetch_html


async def run_single_audit(url: str) -> AuditResult:
    final_url, html = await fetch_html(url, timeout_seconds=settings.request_timeout_seconds)
    seo_score, analytics_score, technical_score, metrics, findings = analyze_page(final_url, html)
    score = round((seo_score * 0.45) + (analytics_score * 0.35) + (technical_score * 0.20))

    summary = (
        f"SEO {seo_score}/100, analytics {analytics_score}/100, technical {technical_score}/100. "
        f"{len(findings)} actionable findings detected."
    )

    return AuditResult(
        url=final_url,
        score=score,
        seo_score=seo_score,
        analytics_score=analytics_score,
        technical_score=technical_score,
        summary=summary,
        metrics=metrics,
        findings=findings,
    )


def build_benchmark(target: AuditResult, competitors: list[AuditResult]) -> BenchmarkSummary:
    if not competitors:
        return BenchmarkSummary(note="No competitors supplied. Benchmarking skipped.")

    best_competitor = max(c.score for c in competitors)
    gap = best_competitor - target.score
    if gap <= 0:
        note = "Target is matching or outperforming provided competitors."
    else:
        note = f"Target trails best competitor by {gap} points. Prioritize high-impact findings first."

    return BenchmarkSummary(best_competitor_score=best_competitor, target_gap=gap, note=note)
