from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class AuditRequest(BaseModel):
    target_url: HttpUrl
    competitor_urls: list[HttpUrl] = Field(default_factory=list)


class Finding(BaseModel):
    id: str
    category: Literal["seo", "analytics", "technical"]
    severity: Literal["critical", "high", "medium", "low"]
    title: str
    why_it_matters: str
    recommendation: str
    effort: Literal["small", "medium", "large"]


class Metric(BaseModel):
    name: str
    value: str | int | float | bool
    passed: bool
    benchmark: str | None = None


class AuditResult(BaseModel):
    url: HttpUrl
    score: int
    seo_score: int
    analytics_score: int
    technical_score: int
    summary: str
    metrics: list[Metric]
    findings: list[Finding]


class BenchmarkSummary(BaseModel):
    best_competitor_score: int | None = None
    target_gap: int | None = None
    note: str


class AuditResponse(BaseModel):
    target: AuditResult
    competitors: list[AuditResult] = Field(default_factory=list)
    benchmark: BenchmarkSummary
