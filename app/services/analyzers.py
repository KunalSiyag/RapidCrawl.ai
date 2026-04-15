from __future__ import annotations

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from app.schemas import Finding, Metric

GA4_PATTERN = re.compile(r"G-[A-Z0-9]{6,}")
UA_PATTERN = re.compile(r"UA-\d+-\d+")
GTM_PATTERN = re.compile(r"GTM-[A-Z0-9]+")


def _severity_to_penalty(severity: str) -> int:
    return {
        "critical": 20,
        "high": 12,
        "medium": 7,
        "low": 3,
    }[severity]


def _score_from_findings(base: int, findings: list[Finding]) -> int:
    score = base - sum(_severity_to_penalty(f.severity) for f in findings)
    return max(0, min(100, score))


def analyze_page(url: str, html: str) -> tuple[int, int, int, list[Metric], list[Finding]]:
    soup = BeautifulSoup(html, "lxml")

    seo_metrics, seo_findings = _analyze_seo(url, soup)
    analytics_metrics, analytics_findings = _analyze_analytics(soup)
    technical_metrics, technical_findings = _analyze_technical(url, soup)

    seo_score = _score_from_findings(100, seo_findings)
    analytics_score = _score_from_findings(100, analytics_findings)
    technical_score = _score_from_findings(100, technical_findings)

    metrics = seo_metrics + analytics_metrics + technical_metrics
    findings = seo_findings + analytics_findings + technical_findings
    return seo_score, analytics_score, technical_score, metrics, findings


def _analyze_seo(url: str, soup: BeautifulSoup) -> tuple[list[Metric], list[Finding]]:
    findings: list[Finding] = []
    metrics: list[Metric] = []

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    title_ok = 35 <= len(title) <= 65
    metrics.append(Metric(name="title_length", value=len(title), passed=title_ok, benchmark="35-65 chars"))
    if not title_ok:
        findings.append(
            Finding(
                id="seo_title_length",
                category="seo",
                severity="high",
                title="Title length is outside optimal range",
                why_it_matters="Search engines rely on titles to understand page relevance and users scan titles in SERPs.",
                recommendation="Keep the title between 35 and 65 characters and include a primary keyword near the beginning.",
                effort="small",
            )
        )

    description_tag = soup.find("meta", attrs={"name": "description"})
    description = description_tag.get("content", "").strip() if description_tag else ""
    desc_ok = 80 <= len(description) <= 160
    metrics.append(Metric(name="meta_description_length", value=len(description), passed=desc_ok, benchmark="80-160 chars"))
    if not desc_ok:
        findings.append(
            Finding(
                id="seo_meta_description",
                category="seo",
                severity="medium",
                title="Meta description is missing or suboptimal",
                why_it_matters="Compelling snippets improve click-through rates from organic search.",
                recommendation="Write a clear 80-160 character meta description with value proposition and CTA.",
                effort="small",
            )
        )

    h1_count = len(soup.find_all("h1"))
    metrics.append(Metric(name="h1_count", value=h1_count, passed=h1_count == 1, benchmark="Exactly 1"))
    if h1_count != 1:
        findings.append(
            Finding(
                id="seo_h1_count",
                category="seo",
                severity="high",
                title="Page should have exactly one H1",
                why_it_matters="A single strong H1 improves content hierarchy and topic clarity.",
                recommendation="Use one descriptive H1 reflecting the page's primary intent.",
                effort="small",
            )
        )

    canonical = soup.find("link", attrs={"rel": "canonical"})
    has_canonical = canonical is not None and bool(canonical.get("href"))
    metrics.append(Metric(name="canonical_tag", value=has_canonical, passed=has_canonical))
    if not has_canonical:
        findings.append(
            Finding(
                id="seo_canonical",
                category="seo",
                severity="medium",
                title="Canonical tag missing",
                why_it_matters="Canonical tags reduce duplicate-content ambiguity for crawlers.",
                recommendation="Set a canonical URL for each indexable page.",
                effort="small",
            )
        )

    images = soup.find_all("img")
    images_with_alt = [img for img in images if img.get("alt", "").strip()]
    alt_ratio = (len(images_with_alt) / len(images)) if images else 1.0
    metrics.append(Metric(name="image_alt_coverage", value=round(alt_ratio * 100, 2), passed=alt_ratio >= 0.9, benchmark=">=90%"))
    if alt_ratio < 0.9:
        findings.append(
            Finding(
                id="seo_alt_attributes",
                category="seo",
                severity="medium",
                title="Image alt-text coverage is low",
                why_it_matters="Alt text improves accessibility and helps image search visibility.",
                recommendation="Add descriptive alt text to informative images.",
                effort="small",
            )
        )

    return metrics, findings


def _analyze_analytics(soup: BeautifulSoup) -> tuple[list[Metric], list[Finding]]:
    findings: list[Finding] = []
    metrics: list[Metric] = []

    html_text = str(soup)
    has_ga4 = bool(GA4_PATTERN.search(html_text))
    has_ua = bool(UA_PATTERN.search(html_text))
    has_gtm = bool(GTM_PATTERN.search(html_text))
    has_plausible = "plausible.io/js/script" in html_text
    has_matomo = "matomo" in html_text.lower()

    metrics.extend(
        [
            Metric(name="ga4_detected", value=has_ga4, passed=has_ga4),
            Metric(name="gtm_detected", value=has_gtm, passed=has_gtm),
            Metric(name="legacy_universal_analytics", value=has_ua, passed=not has_ua),
            Metric(name="privacy_friendly_analytics", value=has_plausible or has_matomo, passed=has_plausible or has_matomo),
        ]
    )

    if not has_ga4 and not has_plausible and not has_matomo:
        findings.append(
            Finding(
                id="analytics_missing_stack",
                category="analytics",
                severity="critical",
                title="No modern analytics stack detected",
                why_it_matters="Without tracking, conversion bottlenecks and channel ROI are invisible.",
                recommendation="Implement GA4 via GTM or a privacy-first stack (e.g., Plausible/Matomo) with event taxonomy.",
                effort="medium",
            )
        )

    if has_ua:
        findings.append(
            Finding(
                id="analytics_ua_present",
                category="analytics",
                severity="high",
                title="Legacy Universal Analytics code detected",
                why_it_matters="UA stopped processing standard hits; data quality and compliance are at risk.",
                recommendation="Remove UA tags and migrate all tracking to GA4/server-side tagging.",
                effort="medium",
            )
        )

    if has_ga4 and not has_gtm:
        findings.append(
            Finding(
                id="analytics_gtm_missing",
                category="analytics",
                severity="low",
                title="GTM not detected",
                why_it_matters="Tag governance and experimentation are slower without centralized tag management.",
                recommendation="Deploy GTM (or server-side tagging) to manage and version tracking tags.",
                effort="small",
            )
        )

    return metrics, findings


def _analyze_technical(url: str, soup: BeautifulSoup) -> tuple[list[Metric], list[Finding]]:
    findings: list[Finding] = []
    metrics: list[Metric] = []

    parsed = urlparse(url)
    https_enabled = parsed.scheme == "https"
    metrics.append(Metric(name="https_enabled", value=https_enabled, passed=https_enabled))
    if not https_enabled:
        findings.append(
            Finding(
                id="tech_https",
                category="technical",
                severity="critical",
                title="HTTPS is not enabled",
                why_it_matters="Search engines and users expect encrypted transport; HTTP harms trust and rankings.",
                recommendation="Force HTTPS with 301 redirects and HSTS.",
                effort="medium",
            )
        )

    has_viewport = soup.find("meta", attrs={"name": "viewport"}) is not None
    metrics.append(Metric(name="mobile_viewport", value=has_viewport, passed=has_viewport))
    if not has_viewport:
        findings.append(
            Finding(
                id="tech_viewport",
                category="technical",
                severity="high",
                title="Viewport meta tag missing",
                why_it_matters="Mobile-first indexing favors responsive pages with proper viewport configuration.",
                recommendation="Add `<meta name='viewport' content='width=device-width, initial-scale=1'>`.",
                effort="small",
            )
        )

    links = [a.get("href", "") for a in soup.find_all("a") if a.get("href")]
    internal_count = 0
    external_count = 0
    for link in links:
        if link.startswith("/"):
            internal_count += 1
        elif link.startswith("http"):
            if parsed.netloc in link:
                internal_count += 1
            else:
                external_count += 1

    metrics.append(Metric(name="internal_links", value=internal_count, passed=internal_count >= 3, benchmark=">=3"))
    metrics.append(Metric(name="external_links", value=external_count, passed=external_count >= 1, benchmark=">=1"))

    if internal_count < 3:
        findings.append(
            Finding(
                id="tech_internal_links",
                category="technical",
                severity="medium",
                title="Internal linking depth is low",
                why_it_matters="Internal links distribute authority and help crawlers discover important pages.",
                recommendation="Add contextual internal links to priority pages and topic clusters.",
                effort="small",
            )
        )

    if external_count < 1:
        findings.append(
            Finding(
                id="tech_external_links",
                category="technical",
                severity="low",
                title="No external authority references",
                why_it_matters="Relevant external references can improve trust and topical association.",
                recommendation="Cite authoritative external resources where relevant.",
                effort="small",
            )
        )

    return metrics, findings
