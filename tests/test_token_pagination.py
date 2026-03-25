import math
import pytest
from fastapi.testclient import TestClient

from webapp.main import app

client = TestClient(app)


class TestTokenPaginationHappyPath:
    def test_default_params(self):
        resp = client.get("/token")
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total"] == 50
        assert data["total_pages"] == 5
        assert len(data["items"]) == 10
        assert all(isinstance(t, str) for t in data["items"])

    def test_custom_params(self):
        resp = client.get("/token", params={"page": 2, "page_size": 5, "total": 12})
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 2
        assert data["page_size"] == 5
        assert data["total"] == 12
        assert data["total_pages"] == 3
        assert len(data["items"]) == 5

    def test_last_page_partial(self):
        resp = client.get("/token", params={"page": 3, "page_size": 5, "total": 12})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_pages"] == 3
        assert len(data["items"]) == 2  # 12 - (2*5) = 2

    def test_page_size_greater_than_total(self):
        resp = client.get("/token", params={"page": 1, "page_size": 100, "total": 7})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_pages"] == 1
        assert len(data["items"]) == 7


class TestTokenPaginationEdgeCases:
    def test_total_zero(self):
        resp = client.get("/token", params={"total": 0})
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["total_pages"] == 0

    def test_page_out_of_range(self):
        resp = client.get("/token", params={"page": 99, "page_size": 10, "total": 10})
        assert resp.status_code == 400
        assert "exceeds total_pages" in resp.json()["detail"]

    def test_page_equals_total_pages(self):
        resp = client.get("/token", params={"page": 2, "page_size": 5, "total": 10})
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 5


class TestTokenPaginationValidation:
    def test_page_zero(self):
        resp = client.get("/token", params={"page": 0})
        assert resp.status_code == 422

    def test_page_negative(self):
        resp = client.get("/token", params={"page": -1})
        assert resp.status_code == 422

    def test_page_size_zero(self):
        resp = client.get("/token", params={"page_size": 0})
        assert resp.status_code == 422

    def test_page_size_exceeds_max(self):
        resp = client.get("/token", params={"page_size": 101})
        assert resp.status_code == 422

    def test_negative_total(self):
        resp = client.get("/token", params={"total": -1})
        assert resp.status_code == 422

    def test_negative_length(self):
        resp = client.get("/token", params={"length": -1})
        assert resp.status_code == 422

    def test_length_zero(self):
        resp = client.get("/token", params={"length": 0})
        assert resp.status_code == 422


class TestTokenLength:
    def test_custom_token_length(self):
        resp = client.get("/token", params={"page_size": 3, "total": 3, "length": 5})
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) == 3
        assert all(len(t) == 5 for t in items)

    def test_default_token_length(self):
        resp = client.get("/token", params={"page_size": 2, "total": 2})
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert all(len(t) == 20 for t in items)
