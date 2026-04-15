from fastapi.testclient import TestClient

from app.main import app


def test_dashboard_page_renders() -> None:
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "RapidCrawl.ai Audit Studio" in response.text
    assert "Run Audit" in response.text
