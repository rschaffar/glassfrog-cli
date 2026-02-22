"""Tests for people commands."""

import json

import httpx
import pytest
import respx
from click.testing import CliRunner

from glassfrog_cli.main import cli

BASE_URL = "https://api.glassfrog.com/api/v3"

PEOPLE_RESPONSE = {
    "people": [
        {
            "id": 50,
            "name": "Alice Smith",
            "email": "alice@example.com",
            "links": {"organizations": [100], "circles": [1, 2]},
        },
        {
            "id": 51,
            "name": "Bob Jones",
            "email": "bob@example.com",
            "links": {"organizations": [100], "circles": [1]},
        },
    ]
}


@pytest.fixture
def runner():
    return CliRunner()


class TestPeopleList:
    @respx.mock
    def test_list_table(self, runner):
        respx.get(f"{BASE_URL}/people").mock(
            return_value=httpx.Response(200, json=PEOPLE_RESPONSE)
        )

        result = runner.invoke(cli, ["--token", "test", "people", "list"])

        assert result.exit_code == 0
        assert "Alice Smith" in result.output
        assert "Bob Jones" in result.output

    @respx.mock
    def test_list_json(self, runner):
        respx.get(f"{BASE_URL}/people").mock(
            return_value=httpx.Response(200, json=PEOPLE_RESPONSE)
        )

        result = runner.invoke(cli, ["--token", "test", "-o", "json", "people", "list"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 2


class TestPeopleShow:
    @respx.mock
    def test_show_table(self, runner):
        respx.get(f"{BASE_URL}/people/50").mock(
            return_value=httpx.Response(
                200,
                json={
                    "people": [
                        {
                            "id": 50,
                            "name": "Alice Smith",
                            "email": "alice@example.com",
                            "links": {"organizations": [100], "circles": [1, 2]},
                        }
                    ]
                },
            )
        )

        result = runner.invoke(cli, ["--token", "test", "people", "show", "50"])

        assert result.exit_code == 0
        assert "Alice Smith" in result.output
        assert "alice@example.com" in result.output
