from __future__ import annotations

import httpx


async def fetch_html(url: str, timeout_seconds: float = 10.0) -> tuple[str, str]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; RapidCrawlBot/1.0; +https://rapidcrawl.ai/bot)"
        )
    }

    async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")

        if "text/html" not in content_type:
            raise ValueError(f"Unsupported content-type '{content_type}' for URL {url}")

        return str(response.url), response.text
