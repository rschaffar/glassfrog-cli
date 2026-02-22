"""Tests for the GlassFrog API client."""

import httpx
import pytest
import respx

from glassfrog_cli.client import GlassFrogClient

TEST_BASE_URL = "https://api.glassfrog.com/api/v3"


@pytest.fixture
def client():
    c = GlassFrogClient(token="test-token", base_url=TEST_BASE_URL)
    yield c
    c.close()


class TestGlassFrogClient:
    @respx.mock
    def test_get_collection(self, client):
        route = respx.get(f"{TEST_BASE_URL}/circles").mock(
            return_value=httpx.Response(
                200,
                json={
                    "circles": [
                        {"id": 1, "name": "General Company"},
                        {"id": 2, "name": "Engineering"},
                    ]
                },
            )
        )

        result = client.get("circles")

        assert route.called
        assert len(result["circles"]) == 2
        assert result["circles"][0]["name"] == "General Company"

    @respx.mock
    def test_get_single_resource(self, client):
        route = respx.get(f"{TEST_BASE_URL}/circles/42").mock(
            return_value=httpx.Response(
                200,
                json={
                    "circles": [{"id": 42, "name": "Engineering"}],
                    "linked": {"roles": [{"id": 100, "name": "Lead Link"}]},
                },
            )
        )

        result = client.get("circles", resource_id=42)

        assert route.called
        assert result["circles"][0]["id"] == 42
        assert result["linked"]["roles"][0]["name"] == "Lead Link"

    @respx.mock
    def test_get_nested_resource(self, client):
        route = respx.get(f"{TEST_BASE_URL}/circles/42/projects").mock(
            return_value=httpx.Response(
                200,
                json={
                    "projects": [
                        {"id": 1, "description": "Build CLI"},
                    ]
                },
            )
        )

        result = client.get_nested("circles", 42, "projects")

        assert route.called
        assert result["projects"][0]["description"] == "Build CLI"

    @respx.mock
    def test_auth_header_sent(self, client):
        route = respx.get(f"{TEST_BASE_URL}/circles").mock(
            return_value=httpx.Response(200, json={"circles": []})
        )

        client.get("circles")

        assert route.calls[0].request.headers["x-auth-token"] == "test-token"

    @respx.mock
    def test_http_error_raised(self, client):
        respx.get(f"{TEST_BASE_URL}/circles/999").mock(
            return_value=httpx.Response(404, json={"error": "Not Found"})
        )

        with pytest.raises(httpx.HTTPStatusError):
            client.get("circles", resource_id=999)

    @respx.mock
    def test_unauthorized_error(self, client):
        respx.get(f"{TEST_BASE_URL}/circles").mock(
            return_value=httpx.Response(401, json={"error": "Unauthorized"})
        )

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            client.get("circles")
        assert exc_info.value.response.status_code == 401

    def test_context_manager(self):
        with GlassFrogClient(token="test-token") as client:
            assert client._token == "test-token"
