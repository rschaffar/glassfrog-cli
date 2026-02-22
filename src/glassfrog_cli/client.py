"""GlassFrog API v3 client."""

from __future__ import annotations

from typing import Any

import httpx

BASE_URL = "https://api.glassfrog.com/api/v3"


class GlassFrogClient:
    """Synchronous HTTP client for the GlassFrog v3 API."""

    def __init__(self, token: str, base_url: str = BASE_URL):
        self._token = token
        self._base_url = base_url
        self._http = httpx.Client(
            base_url=base_url,
            headers={
                "X-Auth-Token": token,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> GlassFrogClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def get(self, resource: str, resource_id: int | None = None) -> dict[str, Any]:
        """GET a resource collection or a single resource by ID.

        Args:
            resource: API resource name (e.g. 'circles', 'roles').
            resource_id: Optional resource ID for single-item fetch.

        Returns:
            Parsed JSON response as a dict.

        Raises:
            httpx.HTTPStatusError: On 4xx/5xx responses.
        """
        if resource_id is not None:
            url = f"/{resource}/{resource_id}"
        else:
            url = f"/{resource}"

        response = self._http.get(url)
        response.raise_for_status()
        return response.json()

    def get_nested(
        self, parent_resource: str, parent_id: int, child_resource: str
    ) -> dict[str, Any]:
        """GET a nested resource (e.g. /circles/123/projects).

        Args:
            parent_resource: Parent resource name.
            parent_id: Parent resource ID.
            child_resource: Child resource name.

        Returns:
            Parsed JSON response as a dict.

        Raises:
            httpx.HTTPStatusError: On 4xx/5xx responses.
        """
        url = f"/{parent_resource}/{parent_id}/{child_resource}"
        response = self._http.get(url)
        response.raise_for_status()
        return response.json()
