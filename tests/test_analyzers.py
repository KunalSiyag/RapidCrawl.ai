from app.services.analyzers import analyze_page


def test_analyze_page_flags_major_issues() -> None:
    html = """
    <html>
      <head>
        <title>Short</title>
      </head>
      <body>
        <h1>Heading One</h1>
        <h1>Heading Two</h1>
        <img src="x.jpg" />
      </body>
    </html>
    """

    seo, analytics, technical, metrics, findings = analyze_page("http://example.com", html)

    assert seo < 100
    assert analytics < 100
    assert technical < 100
    assert any(m.name == "https_enabled" and not m.passed for m in metrics)
    assert any(f.id == "analytics_missing_stack" for f in findings)


def test_analyze_page_detects_healthy_signals() -> None:
    html = """
    <html>
      <head>
        <title>This is a well optimized sample page title for search</title>
        <meta name="description" content="This is a concise but complete meta description for high quality search snippets and click through optimization." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="canonical" href="https://example.com/page" />
      </head>
      <body>
        <h1>Primary heading</h1>
        <img src="a.jpg" alt="alt text" />
        <a href="/one">One</a>
        <a href="/two">Two</a>
        <a href="/three">Three</a>
        <a href="https://external.example.org">External</a>
        <script>window.dataLayer=[];</script>
        <script>var g='G-ABCDEF12';</script>
        <script>var t='GTM-AAAA111';</script>
      </body>
    </html>
    """

    seo, analytics, technical, _, findings = analyze_page("https://example.com", html)

    assert seo >= 90
    assert analytics >= 90
    assert technical >= 90
    assert len(findings) <= 1
