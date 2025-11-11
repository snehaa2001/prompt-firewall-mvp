import pytest
from fastapi.testclient import TestClient

class TestAPI:

    def test_query_clean(self, test_client):
        response = test_client.post(
            "/v1/query",
            json={"prompt": "What is the capital of France?", "model": "gpt-3.5-turbo", "tenantId": "tenant-a"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['decision'] in ['allow', 'warn']

    def test_query_with_pii(self, test_client):
        response = test_client.post(
            "/v1/query",
            json={"prompt": "My email is test@example.com", "model": "gpt-3.5-turbo", "tenantId": "tenant-a"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['decision'] in ['redact', 'block', 'warn']

    def test_get_policies_unauthorized(self, test_client):
        response = test_client.get("/v1/policy")
        assert response.status_code == 401

    def test_get_policies_authorized(self, test_client, mock_firebase_token, admin_headers):
        response = test_client.get("/v1/policy", headers=admin_headers)
        assert response.status_code == 200

    def test_health(self, test_client):
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
