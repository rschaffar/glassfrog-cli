"""Tests for project commands."""

import json

import httpx
import pytest
import respx
from click.testing import CliRunner

from glassfrog_cli.main import cli

BASE_URL = "https://api.glassfrog.com/api/v3"

PROJECTS_RESPONSE = {
    "projects": [
        {
            "id": 200,
            "description": "Build CLI tool",
            "status": "Current",
            "created_at": "2026-01-15T10:00:00Z",
            "archived_at": None,
            "private_to_circle": False,
            "links": {"circle": 1, "person": 50, "role": 12},
        },
        {
            "id": 201,
            "description": "Update docs",
            "status": "Waiting",
            "created_at": "2026-02-01T08:30:00Z",
            "archived_at": None,
            "private_to_circle": False,
            "links": {"circle": 1, "person": 51, "role": 10},
        },
    ]
}


@pytest.fixture
def runner():
    return CliRunner()


class TestProjectsList:
    @respx.mock
    def test_list_by_circle(self, runner):
        respx.get(f"{BASE_URL}/circles/1/projects").mock(
            return_value=httpx.Response(200, json=PROJECTS_RESPONSE)
        )

        result = runner.invoke(
            cli, ["--token", "test", "projects", "list", "--circle", "1"]
        )

        assert result.exit_code == 0
        assert "Build CLI tool" in result.output
        assert "Update docs" in result.output

    @respx.mock
    def test_list_json(self, runner):
        respx.get(f"{BASE_URL}/circles/1/projects").mock(
            return_value=httpx.Response(200, json=PROJECTS_RESPONSE)
        )

        result = runner.invoke(
            cli, ["--token", "test", "-o", "json", "projects", "list", "--circle", "1"]
        )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 2
        assert data[0]["description"] == "Build CLI tool"
