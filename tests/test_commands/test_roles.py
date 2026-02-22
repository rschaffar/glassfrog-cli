"""Tests for role commands."""

import json

import httpx
import pytest
import respx
from click.testing import CliRunner

from glassfrog_cli.main import cli

BASE_URL = "https://api.glassfrog.com/api/v3"

ROLES_RESPONSE = {
    "roles": [
        {
            "id": 10,
            "name": "Lead Link",
            "is_core": True,
            "purpose": "Lead the circle",
            "links": {
                "circle": 1,
                "supporting_circle": None,
                "domains": [],
                "accountabilities": [40],
                "people": [50],
            },
        },
        {
            "id": 12,
            "name": "Developer",
            "is_core": False,
            "purpose": "Write code",
            "links": {
                "circle": 2,
                "supporting_circle": None,
                "domains": [],
                "accountabilities": [],
                "people": [50, 51],
            },
        },
    ],
    "linked": {
        "circles": [{"id": 1, "name": "GCC"}, {"id": 2, "name": "Eng"}],
        "domains": [],
        "accountabilities": [{"id": 40, "description": "Setting priorities"}],
        "people": [
            {"id": 50, "name": "Alice", "email": "alice@example.com"},
            {"id": 51, "name": "Bob", "email": "bob@example.com"},
        ],
    },
}

ROLE_DETAIL_RESPONSE = {
    "roles": [
        {
            "id": 10,
            "name": "Lead Link",
            "is_core": True,
            "purpose": "Lead the circle",
            "links": {
                "circle": 1,
                "supporting_circle": None,
                "domains": [30],
                "accountabilities": [40, 41],
                "people": [50],
            },
        }
    ],
    "linked": {
        "domains": [{"id": 30, "description": "Product roadmap"}],
        "accountabilities": [
            {"id": 40, "description": "Setting priorities"},
            {"id": 41, "description": "Allocating resources"},
        ],
        "people": [{"id": 50, "name": "Alice", "email": "alice@example.com"}],
    },
}


@pytest.fixture
def runner():
    return CliRunner()


class TestRolesList:
    @respx.mock
    def test_list_table(self, runner):
        respx.get(f"{BASE_URL}/roles").mock(
            return_value=httpx.Response(200, json=ROLES_RESPONSE)
        )

        result = runner.invoke(cli, ["--token", "test", "roles", "list"])

        assert result.exit_code == 0
        assert "Lead Link" in result.output
        assert "Developer" in result.output

    @respx.mock
    def test_list_filter_by_circle(self, runner):
        respx.get(f"{BASE_URL}/roles").mock(
            return_value=httpx.Response(200, json=ROLES_RESPONSE)
        )

        result = runner.invoke(cli, ["--token", "test", "roles", "list", "--circle", "2"])

        assert result.exit_code == 0
        assert "Developer" in result.output
        assert "Lead Link" not in result.output

    @respx.mock
    def test_list_json(self, runner):
        respx.get(f"{BASE_URL}/roles").mock(
            return_value=httpx.Response(200, json=ROLES_RESPONSE)
        )

        result = runner.invoke(cli, ["--token", "test", "-o", "json", "roles", "list"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 2


class TestRolesShow:
    @respx.mock
    def test_show_table(self, runner):
        respx.get(f"{BASE_URL}/roles/10").mock(
            return_value=httpx.Response(200, json=ROLE_DETAIL_RESPONSE)
        )

        result = runner.invoke(cli, ["--token", "test", "roles", "show", "10"])

        assert result.exit_code == 0
        assert "Lead Link" in result.output
        assert "Lead the circle" in result.output
        assert "Setting priorities" in result.output
        assert "Alice" in result.output
